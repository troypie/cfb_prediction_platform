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

def transform_stats_to_wide_format(stats):
    """
    Transforms a list of stat objects into a wide-format pandas DataFrame.
    
    :param stats: List of stat objects, each having 'team', 'season', 'conference', 'statName', and 'statValue' attributes.
    :return: A pandas DataFrame in wide format with one row per team-season-conference and columns for each stat.
    """

    # 2. Pivot the data
    # index: These identify the unique row (Team + Season + Conference)
    # columns: These values will become your new headers (e.g., 'firstDowns', 'turnovers')
    # values: The numbers to populate the cells with
    wide_df = df.pivot_table(
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