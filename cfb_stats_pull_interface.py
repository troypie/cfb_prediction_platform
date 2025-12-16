""" main interafece for ETL pipeline """




def pull_team_stats(team_name: str, year: int, start_week: int, end_week: int):
    """
    Pulls all of the team stats for a given team from start week to end week for a given year.
    This function will check to see if data already exists for a given, team, week, 
    and year combination before pulling data and adding it to the database.
    It saves all the data pulled into the postgres database.
    
    :param team_name: name of the team to pull stats for
    :param start_week: beginning week to pull stats for
    :param end_week: ending week to pull stats for
    :param year: season to pull stats for. The year given is the year during the 
    beginning of the season.
    
    """
    pass
    # pull team stats from API

def pull_all_teams_stats(start_week: int, end_week: int, year: int):
    """
    Pulls all of the team stats for all FBS and FCS teams from 
    start week to end week for a given year.
    This function will check to see if data already exists for a given, team, week, 
    and year combination before pulling data and adding it to the database.
    It saves all the data pulled into the postgres database.
    
    :param start_week: beginning week to pull stats for
    :param end_week: ending week to pull stats for
    :param year: season to pull stats for. The year given is the year during the 
    beginning of the season.
    
    """
    pass
    # pull all team stats from API

def pull_player_stats_for_team(team_name: int, start_week: int, end_week: int, year: int):
    """
    Pulls all of the player stats for a given team from start week to end week for a given year.
    This function will check to see if data already exists for a given, player, week, 
    and year combination before pulling data and adding it to the database.
    It saves all the data pulled into the postgres database.
    
    :param team_name: name of the team to pull player stats for
    :param start_week: beginning week to pull stats for
    :param end_week: ending week to pull stats for
    :param year: season to pull stats for. The year given is the year during the 
    beginning of the season.
    
    """
    pass
    # pull player stats from API

def pull_player_stats(player_id: int, start_week: int, end_week: int, year: int):
    """
    Pulls all of the player stats for a given player from start week to end week for a given year.
    This function will check to see if data already exists for a given, player, week, 
    and year combination before pulling data and adding it to the database.
    It saves all the data pulled into the postgres database.
    
    :param player_id: id of the player to pull stats for
    :param start_week: beginning week to pull stats for
    :param end_week: ending week to pull stats for
    :param year: season to pull stats for. The year given is the year during the 
    beginning of the season.
    
    """
    pass
    # pull player stats from API