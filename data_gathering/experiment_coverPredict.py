### ------------------------------------------ ###
# with latest configuration, run experiment. - ###
# ------  Redo so that parameter null or not - ###
# ------- can be passed in. ------------------ ###
### ------------------------------------------ ###

import cfbd
import torch
import torch.nn as nn
import xgboost as xgb
import numpy as np
import json
from typing import List, Dict
from torch.utils.data import DataLoader, TensorDataset



# Load your 2025 embeddings
filename = 'cfb_embeddings_from_gemini_check_format_correct.json'
with open(filename, 'r') as file:
    team_embeddings = json.load(file)

def prepare_classification_data(games: List[cfbd.Game], lines: List[cfbd.GameLine], embeddings: Dict[str, List[float]]):
    X, y = [], []
    # CFBD mapping (simplified for this snippet)
    for g in games:
        line = next((l for l in lines if l.id == g.id), None)

        # check to ensure all data exists for teams
        if (not line or g.home_points is None or g.home_team 
            not in team_embeddings or g.away_team not in team_embeddings):
            continue # skip if any data is missing

        # Features: [Away_Embed, Home_Embed]
        features = team_embeddings[g.away_team] + team_embeddings[g.home_team]
        
        # Labeling Logic:
        # ActualDiff = Away - Home. Spread is usually Home favor (e.g., -7)
        # We define 'Cover' if Away Team beats the spread.
        actual_diff = g.away_points - g.home_points
        spread_target = -line.lines[0].spread 
        
        if actual_diff > spread_target:
            label = 1 # Away Covers
        else:
            label = -1 # Home Covers
        
        X.append(features)
        y.append(label)
    
    return np.array(X), np.array(y)

# --- MODEL 1: XGBOOST ---
def train_xgboost(X_train, y_train):
    # Convert -1, 1 to 0, 1 for XGBoost internal binary, 
    # then apply the 'Too Close' logic post-hoc.
    y_mapped = np.where(y_train == 1, 1, 0)
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method='hist'
    )
    model.fit(X_train, y_mapped)
    return model

# --- MODEL 2: ATTENTION CLASSIFIER ---
class AttentionClassifier(nn.Module):
    def __init__(self, input_dim=4):
        super().__init__()
        self.query = nn.Linear(input_dim, 16)
        self.key = nn.Linear(input_dim, 16)
        self.value = nn.Linear(input_dim, 16)
        self.attn = nn.MultiheadAttention(embed_dim=16, num_heads=4, batch_first=True)
        
        self.classifier = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(64, 2) # Outputs Logits for [Home Covers, Away Covers]
        )

    def forward(self, x):
        # x is [Batch, 8]. Split into Away [Batch, 4] and Home [Batch, 4]
        away, home = x[:, :4], x[:, 4:]
        
        # Transform for Attention
        seq = torch.stack([self.query(away), self.query(home)], dim=1)
        attn_out, _ = self.attn(seq, seq, seq)
        
        # Flatten and classify
        flat = attn_out.reshape(attn_out.shape[0], -1)
        return self.classifier(flat)
    

def train_attention_model(X_train, y_train, epochs=350, batch_size=45):
    # 1. Prepare Data (Map -1, 1 to 0, 1 for CrossEntropy)
    y_mapped = np.where(y_train == 1, 1, 0)
    
    X_tensor = torch.FloatTensor(X_train)
    y_tensor = torch.LongTensor(y_mapped)
    
    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # 2. Initialize Model
    # embed_dim is half of the total feature length (one team)
    embed_dim = X_train.shape[1] // 2
    model = AttentionClassifier(input_dim=embed_dim)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0005, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5)
    criterion = nn.CrossEntropyLoss()
    
    # 3. Training Loop
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(loader):.4f}")
            
    return model

def get_attn_probabailities(model, X_test):
     
    X_tensor = torch.as_tensor(X_test, dtype=torch.float32)

    model.eval()
    with torch.no_grad():
        # Standardize Data (Device-agnostic & Flattened)
        # Get raw logits
        logits = model(X_tensor)
        # Convert to probabilities [128, 2]
        probs = torch.softmax(logits, dim=1)
            
    return probs.cpu().numpy()

# --- CONFIDENCE LOGIC (The <30% Constraint) ---
def get_predictions_fromProbs(probs, threshold_percentile=30):
    """
    Assigns 0 if the model confidence is low.
    Ensures that class 0 is chosen < 30% of the time.
    """

    home_probs = probs[:, 0]
    away_probs = probs[:, 1]
    
    # Calculate margin: distance from a 50/50 toss-up
    confidence = np.abs(away_probs - 0.5)
    threshold = np.percentile(confidence, threshold_percentile)
    
    
    preds = []
    for p, c in zip(away_probs, confidence):
        if c < threshold:
            preds.append(0) # Too close to call
        else:
            preds.append(1 if p > 0.5 else -1)
    return np.array(preds)