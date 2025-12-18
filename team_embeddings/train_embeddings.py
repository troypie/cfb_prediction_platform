
## ML imports
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split

# python imports
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
from typing import Any, List

# custom imports
from postgres_stuff.postgres_config import postgres_connection_string

# database imports
from sqlalchemy import Engine, create_engine


def get_games_data_from_db(engine: Engine) -> pd.DataFrame:
    """
    Retrieves all game data from the cfb_games table in the PostgreSQL database.
    
    :return: A pandas DataFrame containing all game data.
    """
    # define query
    query = "SELECT * FROM cfb_games"

    # execute query and load data into DataFrame
    df = pd.read_sql(query, engine)

    return df

def prepare_game_data(games_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare game data for training the Team2Vec model.
    Returns a cleaned DataFrame with point differentials.
    """
    # only columns needed
    cols = ['home_team', 'home_id', 'home_points', 'away_team', 'away_id', 'away_points']
    df = games_df[cols].copy()
    
    # remove rows where scores are missing (NaN)
    df = df.dropna(subset=['home_points', 'away_points'])
    
    # calculate point_diff
    df['point_diff'] = df['home_points'] - df['away_points']
    
    # remove any resulting NaNs in point_diff
    df = df.dropna(subset=['point_diff'])

    return df

def make_default_team_id_map(games_df: pd.DataFrame) -> dict[str, int]:
    """
    Create a default mapping of team names to unique integer IDs using a DataFrame.
    """
    # get all home team name/ID pairs
    home_teams = games_df[['home_team', 'home_id']].rename(
        columns={'home_team': 'team', 'home_id': 'id'}
    )
    
    # get all away team name/ID pairs
    away_teams = games_df[['away_team', 'away_id']].rename(
        columns={'away_team': 'team', 'away_id': 'id'}
    )
    
    # keep only unique pairs
    all_teams = pd.concat([home_teams, away_teams]).drop_duplicates()
    
    # convert the two columns into a dictionary
    return dict(zip(all_teams['team'], all_teams['id']))

def shuffle_key_order(input_dict: dict[str, int]) -> dict[str, int]:
    """Shuffle the order of keys in a dictionary."""

    new_keys = list(range(len(input_dict.keys())))
    random.shuffle(new_keys)

    shuffled_key_map = {old_key: new_key for new_key, old_key in zip(new_keys, input_dict.keys())}

    return shuffled_key_map

def flip_dict(input_dict: dict[Any, Any]) -> dict[Any, Any]:
    return {v: k for k, v in input_dict.items()}


class Team2Vec(torch.nn.Module):
    """
    Neural network model for learning team embeddings based on game outcomes.
    """

    def __init__(self, num_teams, embedding_dim=6):
        super(Team2Vec, self).__init__()
        self.team_embeddings = torch.nn.Embedding(num_teams, embedding_dim)
        
    def forward(self, home_team_idx, away_team_idx):
        home_embedding = self.team_embeddings(home_team_idx)
        away_embedding = self.team_embeddings(away_team_idx)
        
        # Calculate predicted point differential based on distance between vectors
        return torch.sum(home_embedding - away_embedding, dim=1)
    

def train_team2vec(game_data: pd.DataFrame, team_id_map: dict[str, int],
                    embedding_dim=50, epochs=100):
    """
    Train the Team2Vec model to generate team embeddings.
    
    Args:
        game_data: List of dictionaries with game information
        team_to_id: Dictionary mapping team names to team IDs
        embedding_dim: Dimension of the team embedding vectors
        epochs: Number of training epochs
        
    Returns:
        team_vectors: Dictionary mapping team IDs to embedding vectors
        model: Trained Team2Vec model
        loss_history: List of loss values during training
    """
    
    # Randomize team index
    randomized_team_id_map = shuffle_key_order(team_id_map)
    
    # making tensors, list comprehension saved overhead in time taken to make tensors
    # could speed up if dataframe.map instead of dict list comprehension
    home_indices = torch.tensor(game_data['home_team'].map(randomized_team_id_map).values)
    away_indices = torch.tensor(game_data['away_team'].map(randomized_team_id_map).values)
    point_diffs = torch.tensor(game_data['point_diff'].values, dtype=torch.float)
    
    # Initialize model
    model = Team2Vec(len(randomized_team_id_map), embedding_dim) #get total number of teams
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = torch.nn.MSELoss(reduction='none')
    #loss_fn = torch.nn.MSELoss()
    
    # List to store loss values for plotting
    loss_history = []
    stdv_loss_history = []
    num_training_examples = []

    # Training loop
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        # Forward pass
        predicted_diffs = model(home_indices, away_indices)
        
        # Compute loss
        loss = loss_fn(predicted_diffs, point_diffs)
        avg_loss = torch.mean(loss)
        stdv_loss = torch.std(loss)
        
        # Save the loss for plotting
        loss_history.append(avg_loss.item())
        stdv_loss_history.append(stdv_loss.item())
        num_training_examples.append(len(home_indices))

        # Backward pass
        avg_loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Avg Loss: {avg_loss.item()}")
            print(f"  Loss Variance:     {stdv_loss:.4f}")

    
    # Extract trained embeddings *!*!* ENSURE TEAM VECTORS ARE MAPPED TO CORRECT TEAM NAMES *!*!*
    team_vectors = {}
    with torch.no_grad():
        for team_name, shuffled_id in randomized_team_id_map.items():
            # tensors are assigned to shuffled ids, below gets each shuffled id's vector and the team that it maps to
            # and then converts the original ids to team names
            team_vectors[team_name] = model.team_embeddings(torch.tensor([shuffled_id])).numpy()[0]
    
    return team_vectors, model, loss_history, stdv_loss_history, num_training_examples
    

def plot_training_loss(loss_history, num_training_examples = None, stdv_loss_history = None, save_path=None):
    """
    Plot the training loss history.
    
    Args:
        loss_history: List of loss values during training
        save_path: Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    plt.plot(loss_history)
    if num_training_examples is not None:
        plt.plot(num_training_examples)
    if stdv_loss_history is not None:
        plt.plot(stdv_loss_history)
    plt.title('Team2Vec Training Loss over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (MSE)')
    plt.grid(True)
    
    # Add a smoothed trend line
    if len(loss_history) > 10:
        window_size = min(30, len(loss_history) // 5)
        smoothed = pd.Series(loss_history).rolling(window=window_size, center=True).mean()
        plt.plot(smoothed, 'r--', linewidth=2, label=f'Moving Avg ({window_size} epochs)')
        plt.legend()
    
    # Save the plot if a path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Loss plot saved to {save_path}")
    
    plt.show()
    #plt.close()


# ---- CLI entrypoint  ----
if __name__ == "__main__":
    # Setup the connection engine
    connection_url = postgres_connection_string
    engine = create_engine(connection_url)
    
    # setting up data
    games_df = get_games_data_from_db(engine)
    games_map_df = prepare_game_data(games_df)
    team_id_map = make_default_team_id_map(games_map_df)
    
    # setting hyper parameters
    embedding_dim = 27
    padding_dim = 1
    embedding_epochs = 2200
    prediction_epochs = 500

    # training team2vec embeddings
    team_vectors, model, loss_history, stdv_loss, num_training_examples = train_team2vec(games_map_df, 
                    team_id_map, embedding_dim=embedding_dim, epochs=embedding_epochs)

    team_vectors_df = pd.DataFrame.from_dict(team_vectors, orient='index')
    
    #plot_training_loss(loss_history, num_training_examples, stdv_loss)
    
    # preparing train and test data
    # --- 2. JOINING VECTORS TO GAMES ---
    X_list = []
    y_list = []

    for team_a, team_b, margin in games_map_df[['home_team', 'away_team', 'point_diff']].values:
        # Ensure both teams exist in your vector dictionary
        if team_a in team_vectors and team_b in team_vectors:
            vec_a = team_vectors[team_a]
            vec_b = team_vectors[team_b]
            
            # PADDING: Adding a padding to context vector
            # account for some randomness
            random_val1 = np.random.rand()
            vec_a = np.pad(vec_a, (0, padding_dim), 'constant', constant_values=random_val1)
            random_val2 = np.random.rand()
            vec_b = np.pad(vec_b, (0, padding_dim), 'constant', constant_values=random_val2)
            
                
            X_list.append([vec_a, vec_b])
            y_list.append([margin])

    # Convert to Numpy then to Tensors
    X = np.array(X_list, dtype=np.float32) # Shape: (NumGames, 2, 8)
    y = np.array(y_list, dtype=np.float32) # Shape: (NumGames, 1)

    # --- 3. CREATE TRAIN/TEST SPLITS ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Convert to PyTorch Tensors
    X_train = torch.from_numpy(X_train)
    y_train = torch.from_numpy(y_train)
    X_test = torch.from_numpy(X_test)
    y_test = torch.from_numpy(y_test)

    print(f"Training on {X_train.shape[0]} games.")
    print(f"Testing on {X_test.shape[0]} games.")
    

    # training attentin model
    class MiniTransformer(nn.Module):
        def __init__(self):
            super(MiniTransformer, self).__init__()
            # 1. Attention Layer: 8-dim input, 1 head is enough for this size
            self.attention = nn.MultiheadAttention(embed_dim=embedding_dim + padding_dim,
                                                    num_heads=1, batch_first=True)
            
            # 2. Feed Forward Network (FFN)
            # Input to FFN: (2 tokens * 8 dims) = 16 
            self.ffn = nn.Sequential(
                nn.Linear((embedding_dim + padding_dim) * 2, 32),   # Hidden layer
                nn.ReLU(),
                nn.Linear(32, 1)     # Final output: single float
            )

        def forward(self, x):
            # MultiheadAttention returns (output, weights)
            attn_output, _ = self.attention(x, x, x)
            
            # Flatten the two 8-dim tokens into one 16-dim vector
            flattened = attn_output.reshape(attn_output.shape[0], -1)
            
            # Pass through Feed Forward
            return self.ffn(flattened)

    # 2. Setup Data, Model, and Optimizer
    model = MiniTransformer()
    criterion = torch.nn.MSELoss(reduction='none') #nn.MSELoss()  # Mean Squared Error for regression
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    nn_loss_history = []
    nn_var_history = []
    # 3. The Training Loop
    for epoch in range(prediction_epochs):
        model.train()
        
        # Clear gradients
        optimizer.zero_grad()
        
        # Forward pass
        predictions = model(X_train)
        
        # Compute loss
        loss = criterion(predictions, y_train)
        avg_loss = torch.mean(loss)
        var_loss = torch.var(loss)
        nn_loss_history.append(avg_loss.item())
        nn_var_history.append(var_loss.item())
        
        # Backward pass (calculate gradients)
        avg_loss.backward()
        
        # Update weights
        optimizer.step()
        
        if (epoch + 1) % 50 == 0:
            print(f'Epoch [{epoch+1}/{prediction_epochs}], Loss: {avg_loss.item():.4f}')
    
    print("Training Complete!")


    plot_training_loss(nn_loss_history)
    


    # 4. TODO: Evaluate on Test Set
    model.eval()
    with torch.no_grad():
        predictions = model(X_test)
        if predictions.shape != y_test.shape:
            # below fixes size diff if both objects have the same number of entires
            # fixes size without moving any blocks of memory
            y_test = y_test.view_as(predictions)

        errors = predictions - y_test
        mse = torch.mean((errors)**2)
        mae = torch.mean(torch.abs(errors))
        var_me = torch.var(errors)

        print(f"Test MSE: {mse.item():.4f}")
        print(f"Test MAE (Avg Point Error): {mae.item():.4f}")
        print(f"Test Error Variance: {var_me.item():.4f}")
    
    
    # TODO add game prediction method
    # predicting games function
    def predict_game(home_team_name, away_team_name, model, team_vectors_dict):
        """
        Retrieves team vectors, formats them, and returns a margin prediction.
        """
        # 1. Ensure model is in evaluation mode (important for attention layers)
        model.eval()
        
        # 2. Retrieve vectors from your dictionary
        try:
            vec_h = team_vectors_dict[home_team_name]
            vec_a = team_vectors_dict[away_team_name]
        except KeyError as e:
            return f"Error: Team {e} not found in the vector dictionary."

       # PADDING: Adding a padding
        random_val1 = np.random.rand()
        vec_h = np.pad(vec_h, (0, padding_dim), 'constant', constant_values=random_val1)
        random_val2 = np.random.rand()
        vec_a = np.pad(vec_a, (0, padding_dim), 'constant', constant_values=random_val2)

        # 4. Convert to Tensor and add Batch Dimension (1, 2, 8)
        # Shape becomes: [Batch Size, Number of Tokens, Parameters per Token]
        input_tensor = torch.tensor([vec_h, vec_a], dtype=torch.float32).unsqueeze(0)

        # 5. Get Prediction
        with torch.no_grad():
            prediction = model(input_tensor)
        
        return prediction.item()

    # predicting a game
    margin = predict_game('Texas A&M', 'Miami', model, team_vectors)
    print(f"Predicted Margin: {margin:.2f}")


    # TODO Test with: 
    #   1.) Current embedding method, 
    #   2.) GPT Embedding method:
    #       Gemini Embeddings
    #       French company embeddings
    #       Claude embeddings
    #       Chat GPT embeddings
    #       Test mebeddings made via different prompts?
    #   3.) Dropout embedding method

    

'''
    #vector_file_name = f'/team2vec_embeddings_edim{embedding_dim}_epochs{epochs}.csv'
    
    #team_vectors_df.index.name = 'team_name'
    #team_vectors_df.to_csv(experiment_output_path + vector_file_name)
    
    #graph_file_name = f'/team2vec_training_loss_plot_edim{embedding_dim}_epochs{epochs}.png'
    
    #print(f"Experiment results saved to {experiment_output_path}")
    #print(f"Team graph saved to {graph_file_name}")
    #print(f"Team vectors saved to {vector_file_name}")
'''