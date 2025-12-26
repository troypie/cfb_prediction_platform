


import torch
import torch.nn as nn
import xgboost as xgb
import numpy as np
import json
from torch.utils.data import DataLoader, TensorDataset

# Load your 2025 embeddings
filename = 'cfb_embeddings_from_gemini_check_format_correct.json'
with open(filename, 'r') as file:
    team_embeddings = json.load(file)


def prepare_classification_data(games, lines, embeddings):
    X, y = [], []
    # CFBD mapping (simplified for this snippet)
    for g in games:
        line = next((l for l in lines if l.id == g.id), None)
        if not line or g.home_points is None: continue
        
        # Features: [Away_Embed, Home_Embed]
        features = embeddings[g.away_team] + embeddings[g.home_team]
        
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

# --- MODEL 1: SOTA XGBOOST ---
def train_xgboost(X_train, y_train):
    # Convert -1, 1 to 0, 1 for XGBoost internal binary, 
    # then we apply the 'Too Close' logic post-hoc.
    y_mapped = np.where(y_train == 1, 1, 0)
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method='hist' # SOTA performance
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
        self.attn = nn.MultiheadAttention(embed_dim=16, num_heads=2, batch_first=True)
        
        self.classifier = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
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

# --- CONFIDENCE LOGIC (The <30% Constraint) ---
def get_constrained_predictions(probs, threshold_percentile=30):
    """
    Assigns 0 if the model confidence is low.
    Ensures that class 0 is chosen < 30% of the time.
    """
    # Calculate margin: distance from a 50/50 toss-up
    confidence = np.abs(probs - 0.5)
    threshold = np.percentile(confidence, threshold_percentile)
    
    preds = []
    for p, c in zip(probs, confidence):
        if c < threshold:
            preds.append(0) # Too close to call
        else:
            preds.append(1 if p > 0.5 else -1)
    return np.array(preds)

