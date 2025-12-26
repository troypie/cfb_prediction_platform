# get training data for experiment

# includes api calls and labeled data preparation


import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import json
import numpy as np

#Api & Key
import cfbd
import cfb_api_key


# Defining the host is optional and defaults to https://api.collegefootballdata.com
# See configuration.py for a list of all supported configuration parameters.
configuration = cfbd.Configuration(
    host = "https://api.collegefootballdata.com"
)
# Configure Bearer authorization: apiKey
configuration = cfbd.Configuration(
    access_token = cfb_api_key.cfbd_api_key
)

# --- 1. API Functions ---
def get_games(year: int, week: int | None = None):
    
    with cfbd.ApiClient(configuration) as api_client:
        
        api_instance = cfbd.GamesApi(api_client)
        
        try:
            if week is None:
                return api_instance.get_games(year=year)
            else:
                return api_instance.get_games(year=year, week=week)
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []


def get_lines(year: int, week: int | None = None):
    
    with cfbd.ApiClient(configuration) as api_client:
        api_instance = cfbd.BettingApi(api_client)
        try:
            return api_instance.get_lines(year=year, week=week)
        except Exception as e:
            print(f"Error fetching lines: {e}")
            return []
        
# custom function
# returns 
def get_data(year_start: int, year_end: int | None = None):
    for week in range(1, 16):
        games = get_games(year, week)
        lines = get_lines(year, week)

    return games, lines

def get_data_gameScores_Lines(year_start: int, year_end: int | None = None):
    all_games = []
    all_lines = []

    # check year end
    if year_end is None:
        year_end = year_start + 1


    # Loop through each year in the range (inclusive)
    for year in range(year_start, year_end):
        print(f"Fetching data for {year}...")
        
        games = get_games(year)
        lines = get_lines(year)
            
        # Use extend to add the lists together
        if games:
            all_games.extend(games)
        if lines:
            all_lines.extend(lines)

    return all_games, all_lines
'''
# --- 2. Data Preparation ---
def get_score_data_with_lines(year=2025):
    X_away, X_home, y_diff, y_spreads = [], [], [], []
    embeddings = json.loads(team_embeddings_json) # Your JSON here
    
    for week in range(1, 16):
        games = get_games(year, week)
        lines = get_lines(year, week)
        
        # Create a lookup for spreads by game ID
        # Note: We take the first available provider's spread (usually consensus)
        line_map = {l.id: l.lines[0].spread for l in lines if l.lines}
        
        for g in games:
            if g.id in line_map and g.home_points is not None:
                if g.home_team in embeddings and g.away_team in embeddings:
                    X_away.append(embeddings[g.away_team])
                    X_home.append(embeddings[g.home_team])
                    y_diff.append(float(g.away_points - g.home_points))
                    # CFBD Spread is typically for the Home Team (e.g., -7 means Home is favored)
                    y_spreads.append(float(line_map[g.id]))
                
    return (torch.tensor(X_away), torch.tensor(X_home), 
            torch.tensor(y_diff).unsqueeze(1), torch.tensor(y_spreads).unsqueeze(1))
'''