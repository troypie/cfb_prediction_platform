import os

# cfb stats api
import cfbd
from cfbd.rest import ApiException
from pprint import pprint

# custom imports
from api_utils import transform_stats_to_wide_format, make_key_value_df_from_stats


#Api Key
api_key = "xkdLaiEmeJaK3JeZvRZ+cuTT30SMpoJhqwMxBnvDp2mwHWUi8sgj1Lc35bHBqb3X"
# Defining the host is optional and defaults to https://api.collegefootballdata.com
# See configuration.py for a list of all supported configuration parameters.
configuration = cfbd.Configuration(
    access_token = api_key
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


with cfbd.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cfbd.GamesApi(api_client)
    year = 56 # int | Required year filter (except when id is specified) (optional)
    week = 56 # int | Optional week filter (optional)
    season_type = cfbd.SeasonType() # SeasonType | Optional season type filter (optional)
    classification = cfbd.DivisionClassification() # DivisionClassification | Optional division classification filter (optional)
    team = 'team_example' # str | Optional team filter (optional)
    home = 'home_example' # str | Optional home team filter (optional)
    away = 'away_example' # str | Optional away team filter (optional)
    conference = 'conference_example' # str | Optional conference filter (optional)
    id = 56 # int | Game id filter to retrieve a single game (optional)

    try:
        api_response = api_instance.get_games(year=year, week=week, season_type=season_type, classification=classification, team=team, home=home, away=away, conference=conference, id=id)
        print("The response of GamesApi->get_games:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GamesApi->get_games: %s\n" % e)


stats = get_team_stats(2025, start_week=1, end_week=3)
if stats is not None:
    stats_df = make_key_value_df_from_stats(stats)
    transform_stats_to_wide_format(stats_df)