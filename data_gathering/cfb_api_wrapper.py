import os
import pandas as pd
from sqlalchemy import create_engine

# cfb stats api
import cfbd
from cfbd.rest import ApiException
from pprint import pprint

# custom imports
import api_utils as utils
import cfb_api_key
from postgres_stuff.postgres_config import postgres_config


# Defining the host is optional and defaults to https://api.collegefootballdata.com
# See configuration.py for a list of all supported configuration parameters.
configuration = cfbd.Configuration(
    access_token = cfb_api_key.cfbd_api_key
)


### --- Example API call for betting lines --- ###
def get_betting_lines():
    api_response = None
    # Enter a context with an instance of the API client
    with cfbd.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = cfbd.BettingApi(api_client)
        game_id = 56 # int | Optional gameId filter (optional)
        year = 2025 # int | Year filter, required if game id not specified (optional)
        #season_type = cfbd.SeasonType() # SeasonType | Optional season type filter (optional)
        week = 3 # int | Optional week filter (optional)
        team = 'team_example' # str | Optional team filter (optional)
        home = 'home_example' # str | Optional home team filter (optional)
        away = 'away_example' # str | Optional away team filter (optional)
        conference = 'conference_example' # str | Optional conference filter (optional)
        provider = 'provider_example' # str | Optional provider name filter (optional)

        try:
            api_response = api_instance.get_lines(year=year, week=week)
            print("The response of BettingApi->get_lines:\n")
        except Exception as e:
            print("Exception when calling BettingApi->get_lines: %s\n" % e)
    
    return api_response

# call the function
#pprint(get_betting_lines())

# example response
"""
BettingGame(id=401767131, season=2025, season_type=<SeasonType.REGULAR: 'regular'>,
 week=3, start_date=datetime.datetime(2025, 9, 14, 1, 0, tzinfo=datetime.timezone.utc),
 home_team_id=16, home_team='Sacramento State', home_conference='Big Sky',
 home_classification=<DivisionClassification.FCS: 'fcs'>, home_score=49,
 away_team_id=2385, away_team='Mercyhurst', away_conference='NEC',
 away_classification=<DivisionClassification.FCS: 'fcs'>, away_score=28,
 lines=[GameLine(provider='ESPN Bet', spread=-21.5,
 formatted_spread='Sacramento State -21.5', spread_open=None, over_under=57.5,
 over_under_open=None, home_moneyline=None, away_moneyline=None)]) 
"""
### ------ ###



### --- Example API call for user info --- ###
def get_user_info():
    api_response = None
    # Enter a context with an instance of the API client
    with cfbd.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = cfbd.InfoApi(api_client)

        try:
            api_response = api_instance.get_user_info()
            print("The response of InfoApi->get_user_info:\n")
        except Exception as e:
            print("Exception when calling InfoApi->get_user_info: %s\n" % e)

    return api_response

# call the function
#pprint(get_user_info())

# example response
"""
The response of InfoApi->get_user_info:

UserInfo(patron_level=0, remaining_calls=2998)
"""
### ------ ###


### --- Example API call to get teams --- ###
def get_teams():
    api_response = None
    with cfbd.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = cfbd.TeamsApi(api_client)
        conference = 'conference_example' # str | Optional conference abbreviation filter (optional)
        year = 2025 # int | Optional year filter to get historical conference affiliations (optional)

        try:
            api_response = api_instance.get_teams()
            print("The response of TeamsApi->get_teams:\n")
        except Exception as e:
            print("Exception when calling TeamsApi->get_teams: %s\n" % e)

    return api_response

# example response
"""
Team(id=2588, school='Southwestern University', mascot='Pirates',
 abbreviation='SW', alternate_names=['Southwestern (TX)', 'SW', 'SW Univ'],
 conference='Southern Athletic', division=None, classification='iii',
 color='#null', alternate_color='#ffcd00',
 logos=['http://a.espncdn.com/i/teamlogos/ncaa/500/2588.png',
 'http://a.espncdn.com/i/teamlogos/ncaa/500-dark/2588.png'], twitter=None,
 location=Venue(id=6118, name='Birkelbach Field', city='Georgetown',
 state='TX', zip='78633', country_code='US', timezone=None,
 latitude=30.6326942, longitude=-97.6772311, elevation=None, capacity=12442,
 construction_year=None, grass=None, dome=False))
"""
### ------ ###


def get_team_stats(year, start_week=0, end_week=16):
    api_response = None
    team = 'team_example' # str | Team filter, required if year not specified (optional)
    conference = 'conference_example' # str | Optional conference filter (optional)
    
    with cfbd.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = cfbd.StatsApi(api_client)

        try:
            api_response = api_instance.get_team_stats(year=year, start_week=start_week, end_week=end_week)
        except Exception as e:
            print("Exception when calling StatsApi->get_team_stats: %s\n" % e)

    return api_response


def get_games(year: int, week : int | None = None):
    api_response = None
    with cfbd.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = cfbd.GamesApi(api_client)
        #year = 2025 # int | Required year filter (except when id is specified) (optional)
        #week = 3 # int | Optional week filter (optional)
        #season_type = cfbd.SeasonType() # SeasonType | Optional season type filter (optional)
        #classification = cfbd.DivisionClassification() # DivisionClassification | Optional division classification filter (optional)
        #team = 'team_example' # str | Optional team filter (optional)
        #home = 'home_example' # str | Optional home team filter (optional)
        #away = 'away_example' # str | Optional away team filter (optional)
        #conference = 'conference_example' # str | Optional conference filter (optional)
        #id = 56 # int | Game id filter to retrieve a single game (optional)

        try:
            api_response = api_instance.get_games(year=year, week=week)
        except Exception as e:
            print("Exception when calling GamesApi->get_games: %s\n" % e)
        
    return api_response

def get_player_stats(year: int, start_week: int, end_week: int):
    api_response = None
    with cfbd.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = cfbd.StatsApi(api_client)
        #year = 2025 # int | Required year filter
        #conference = 'conference_example' # str | Optional conference filter (optional)
        #team = 'team_example' # str | Optional team filter (optional)
        #start_week = 1 # int | Optional starting week range (optional)
        #end_week = 3 # int | Optional ending week range (optional)
        #season_type = cfbd.SeasonType() # SeasonType | Optional season type filter (optional)
        #category = 'category_example' # str | Optional category filter (optional)

        try:
            api_response = api_instance.get_player_season_stats(year, start_week=start_week, end_week=end_week)
        except Exception as e:
            print("Exception when calling StatsApi->get_player_season_stats: %s\n" % e)

        return api_response



# --- Postgres Config ---
config = postgres_config

def upload_games_to_postgres(df, db_config):
    """
    Uploads a DataFrame to the 'games' table in PostgreSQL.
    
    :param df: pandas DataFrame containing game data
    :param db_config: dictionary with keys 'user', 'password', 'host', 'port', 'dbname'
    """
    table_name = 'cfb_games'
    try:
        # 1. Create the connection string (URL)
        # Format: postgresql://username:password@host:port/database
        connection_url = (
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
        )
        
        # 2. Create the SQLAlchemy engine
        engine = create_engine(connection_url)
        
        # 3. Upload the data
        # 'if_exists=append' ensures we don't delete the table, just add rows
        # 'index=False' prevents pandas from creating a column for the DF index
        df.to_sql(table_name, engine, if_exists='append', index=False)
        
        print(f"Successfully uploaded {len(df)} rows to the games table.")
        
    except Exception as e:
        print(f"An error occurred: {e}")


# ---- CLI entrypoint  ----
if __name__ == "__main__":

    '''
    # example of get team stats
    stats = get_team_stats(2025, start_week=1, end_week=3)
    if stats is not None:
        stats_df = utils.make_key_value_df_from_stats(stats)
        states_final_df = utils.transform_stats_to_wide_format(stats_df)
    '''
        
    # example of get games and upload them to postgres
    games = get_games(2025)
    games_df = utils.games_to_df(games)
    pprint(games_df.head())
    #upload_games_to_postgres(games_df, config)

    # upload_games_to_postgres(my_games_df, config)

    '''
    # example of get player stats
    stats = get_player_stats(2025, start_week=1, end_week=3)
    if stats is not None:
        stats_df = utils.make_key_value_df_from_stats(stats)
        stats_final_df = utils.transform_player_stats_to_wide(stats_df)
        print(stats_final_df)
    '''

