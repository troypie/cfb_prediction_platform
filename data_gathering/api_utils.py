import pandas as pd

def make_key_value_df_from_stats(stats):
    """
    Transforms a list of stat objects into a pandas DataFrame with columns of:
        conference, season, statName, statValue, team
    
    :param stats: List of stat objects, each having 'statName' and 'statValue' attributes.
    :return: A pandas DataFrame DataFrame with columns of:
        conference, season, statName, statValue, team
    """
    stats_dicts = [stat.to_dict() for stat in stats]
    df = pd.DataFrame(stats_dicts)

    return df

def transform_team_stats_to_wide_format(stats: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms a list of stat objects into a wide-format pandas DataFrame.
    
    :param stats: List of stat objects, each having 'team', 'season', 'conference', 'statName', and 'statValue' attributes.
    :return: A pandas DataFrame in wide format with one row per team-season-conference and columns for each stat.
    """

    # 2. Pivot the data
    # index: These identify the unique row (Team + Season + Conference)
    # columns: These values will become your new headers (e.g., 'firstDowns', 'turnovers')
    # values: The numbers to populate the cells with
    wide_df = stats.pivot_table(
        index=['team', 'season', 'conference'], 
        columns='statName', 
        values='statValue'
    )

    # 3. Clean up
    # Fill empty stats with 0 (optional, but recommended for SQL)
    wide_df = wide_df.fillna(0)

    # Flatten the index so 'team', 'season', etc. become normal columns again
    wide_df = wide_df.reset_index()
    return wide_df


def transform_player_stats_to_wide(stats: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms a list of PlayerStat objects into a wide-format pandas DataFrame.
    """
    # Convert the numerical stat value from string to float/numeric
    stats['stat'] = pd.to_numeric(stats['stat'], errors='coerce')

    # Create a new column for the stat category to use as pivot columns
    stats['stat_col_name'] = stats['category']

    # Pivot the data
    # Index: Defines the unique row (Season + Player ID)
    wide_df = stats.pivot_table(
        index=['season', 'playerId'],
        columns='stat_col_name',
        values='stat'
    )

    # Clean up: Fill empty values with 0 and reset index to flatten the table
    wide_df = wide_df.fillna(0).reset_index()
    
    # Optional: Remove the index name created by the pivot columns
    wide_df.columns.name = None
    
    return wide_df



def games_to_df(games_list):
    """
    Converts a list of Game objects into a Pandas DataFrame ready for PostgreSQL.
    """
    data = []

    for game in games_list:
        row = {
            'id': game.id,
            'season': game.season,
            'week': game.week,
            # Extract .value from Enums if present, otherwise fallback to string
            'season_type': getattr(game.season_type, 'value', str(game.season_type)),
            
            'start_date': game.start_date,
            'start_time_tbd': game.start_time_tbd,
            'completed': game.completed,
            'neutral_site': game.neutral_site,
            'conference_game': game.conference_game,
            'attendance': game.attendance,
            'venue_id': game.venue_id,
            'venue': game.venue,
            
            'home_id': game.home_id,
            'home_team': game.home_team,
            'home_conference': game.home_conference,
            'home_classification': getattr(game.home_classification, 'value', str(game.home_classification)),
            'home_points': game.home_points,
            'home_line_scores': game.home_line_scores, # Pandas stores this as object (list)
            'home_postgame_win_probability': game.home_postgame_win_probability,
            'home_pregame_elo': game.home_pregame_elo,
            'home_postgame_elo': game.home_postgame_elo,
            
            'away_id': game.away_id,
            'away_team': game.away_team,
            'away_conference': game.away_conference,
            'away_classification': getattr(game.away_classification, 'value', str(game.away_classification)),
            'away_points': game.away_points,
            'away_line_scores': game.away_line_scores,
            'away_postgame_win_probability': game.away_postgame_win_probability,
            'away_pregame_elo': game.away_pregame_elo,
            'away_postgame_elo': game.away_postgame_elo,
            
            'excitement_index': game.excitement_index,
            'highlights': game.highlights,
            'notes': game.notes
        }
        data.append(row)

    df = pd.DataFrame(data)
    return df