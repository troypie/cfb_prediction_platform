
## ML imports
import torch

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

def prepare_game_data(games_df: pd.DataFrame) -> List[dict]:
    """
    Prepare game data for training the Team2Vec model.
    By finding point differentials between home team - away team, 
    and then returning a minimal data frame that only has the columns 
    needed for training.
    
    Args:
        games_df: DataFrame containing game data from db
        
    Returns:
        game_data: List of dictionaries with values for:
          home team, home team id, away team, away team id, point difference of game 
    """
    
    # Extract relevant information: team pairs and point differentials
    game_data = []
    for _, game in games_df.iterrows():
        home_team = game['home_team']
        home_team_id = game['home_id']
        away_team = game['away_team']
        away_team_id = game['away_id']
        home_score = game['home_points']
        away_score = game['away_points']
        
        point_diff = home_score - away_score
        
            
        game_data.append({
            'home_team': home_team,
            'home_team_id': home_team_id,
            'away_team': away_team,
            'away_team_id': away_team_id,
            'point_diff': point_diff
        })
    
    return game_data

def make_default_team_id_map(games_dict: List[dict[str, int]]) -> dict[str, int]:
    """
    Create a default mapping of team names to unique integer IDs.
    
    Args:
        games_dict: List of dictionaries with game information
        
    Returns:
        team_id_map: Dictionary mapping team names to unique integer IDs
    """
    team_id_map = dict()
    for game in games_dict:
        team_id_map[game['home_team']] = game['home_team_id']
        team_id_map[game['away_team']] = game['away_team_id']
    
    return team_id_map

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
    

def train_team2vec(game_data: List[dict], team_id_map: dict[str, int],
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
    
    # Randomize team index and then turn into tensor, also turn point diff into a float tensor
    randomized_team_id_map = shuffle_key_order(team_id_map)
    # saved flipped team id map, so we can revert after training vectors
    flipped_randaomized_team_id_map = flip_dict(randomized_team_id_map)
    
    # making tensors, list comprehension saved overhead in time taken to make tensors
    # could speed up if dataframe.map instead of dict list comprehension
    home_indices = torch.tensor([randomized_team_id_map[game['home_team']] for game in game_data])
    away_indices = torch.tensor([randomized_team_id_map[game['away_team']] for game in game_data])
    point_diffs = torch.tensor([game['point_diff'] for game in game_data], dtype=torch.float)
    
    # Initialize model
    model = Team2Vec(len(randomized_team_id_map), embedding_dim) #get total number of teams
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = torch.nn.MSELoss()
    
    # List to store loss values for plotting
    loss_history = []
    
    # Training loop
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        # Forward pass
        predicted_diffs = model(home_indices, away_indices)
        
        # Compute loss
        loss = loss_fn(predicted_diffs, point_diffs)
        
        # Save the loss for plotting
        loss_history.append(loss.item())
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item()}")

    
    # Extract trained embeddings *!*!* ENSURE TEAM VECTORS ARE MAPPED TO CORRECT TEAM NAMES *!*!*
    team_vectors = {}
    with torch.no_grad():
        for team_name, shuffled_id in randomized_team_id_map.items():
            # tensors are assigned to shuffled ids, below gets each shuffled id's vector and the team that it maps to
            # and then converts the original ids to team names
            team_vectors[team_name] = model.team_embeddings(torch.tensor([shuffled_id])).numpy()[0]
    
    return team_vectors, model, loss_history  
    

def plot_training_loss(loss_history, save_path=None):
    """
    Plot the training loss history.
    
    Args:
        loss_history: List of loss values during training
        save_path: Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    plt.plot(loss_history)
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
    
    plt.close()


# ---- CLI entrypoint  ----
if __name__ == "__main__":
    # Setup the connection engine
    connection_url = postgres_connection_string
    engine = create_engine(connection_url)
    
    games_df = get_games_data_from_db(engine)
    games_dicts = prepare_game_data(games_df)
    print(games_dicts)
    
    '''
    team_id_map = make_default_team_id_map(games_dicts)
    
    
    embedding_dim = 20
    epochs = 100
    # train the model
    team_vectors, model, loss_history = train_team2vec(games_dicts, team_id_map, 
                                                       embedding_dim=embedding_dim, epochs=epochs)
    '''
    #vector_file_name = f'/team2vec_embeddings_edim{embedding_dim}_epochs{epochs}.csv'
    #team_vectors_df = pd.DataFrame.from_dict(team_vectors, orient='index')
    #team_vectors_df.index.name = 'team_name'
    #team_vectors_df.to_csv(experiment_output_path + vector_file_name)
    
    #graph_file_name = f'/team2vec_training_loss_plot_edim{embedding_dim}_epochs{epochs}.png'
    #plot_training_loss(loss_history, save_path=experiment_output_path + graph_file_name)
    #print(f"Experiment results saved to {experiment_output_path}")
    #print(f"Team graph saved to {graph_file_name}")
    #print(f"Team vectors saved to {vector_file_name}")
