from pymongo import MongoClient
from pandas import DataFrame
import json
import certifi

from .data_retrieval import get_player_rating

def database_connect():
    # Read from file
    with open('db_conn.json') as json_file:
        db_conn_json = json.load(json_file)

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(
        host='mongodb+srv://mtcars.cjqmp.mongodb.net',
        username=db_conn_json['username'],
        password=db_conn_json['password'],
        tlsCAFile=certifi.where()
    )

    # Create the database for our example (we will use the same database throughout the tutorial
    return client
    
def convert_to_df(mongo_collection):
    cursor = mongo_collection.find()
    list_cur = list(cursor)
    df = DataFrame(list_cur)
    return df

def get_aoe_league_data_depreciated(mongo_clientd):
    # Retrieve DB
    database = mongo_clientd['mtcars']

    # Access to two databases
    team_collection = database['test_collection']
    match_collection = database['matches']
    
    # Switch them to dataframes
    team_df = convert_to_df(team_collection)
    match_df = convert_to_df(match_collection)

    # Format the same names and drop extra columns
    team_df.drop('Division Season 3', axis=1, inplace=True)
    team_df.drop('avg_avg_rating_rm', axis=1, inplace=True)
    team_df.drop('avg_avg_rating_tg', axis=1, inplace=True)
    team_df.drop('avg_crt_rating_rm', axis=1, inplace=True)
    team_df.drop('avg_crt_rating_tg', axis=1, inplace=True)
    team_df.drop('Seeding', axis=1, inplace=True)

    match_df.drop('Captain', axis=1, inplace=True)
    match_df.drop('set', axis=1, inplace=True)
    match_df.drop('start_date', axis=1, inplace=True)
    match_df.drop('calender_week', axis=1, inplace=True)
    match_df.drop('Tournament_week', axis=1, inplace=True)
    match_df.drop('Seeding', axis=1, inplace=True)
    match_df.drop('submitted', axis=1, inplace=True)
    match_df.drop('game', axis=1, inplace=True)
    match_df.drop('map', axis=1, inplace=True)
    match_df.drop('submitted_by', axis=1, inplace=True)
    match_df.drop('submit_date', axis=1, inplace=True)
    match_df.rename(columns={'winner': 'Winner', 'loser': 'Loser', 'game_id': 'Game ID'}, inplace=True)

    return team_df, match_df

def get_aoe_league_data(mongo_clientd):
    # Retrieve DB
    database = mongo_clientd['s5_loe']

    # Access to two databases
    team_collection = database['teams_registered']
    set_collection = database['sets']
    match_collection = database['matches']

    # Switch them to dataframes
    team_df = convert_to_df(team_collection)
    set_df = convert_to_df(set_collection)
    match_df = convert_to_df(match_collection)

    # Construct team df with info from both
    PLAYER_KEYS = {'nameDiscord', 'aoe2Id'}
    final_team_df = DataFrame(columns=['Team Name', 'Player', 'Division'])
    df_index = 0
    for team_name, player in zip(team_df['teamName'], team_df['player']):
        # Get division from set table, can do this since everyone will have at least 1 home game
        home_division = set_df[set_df['Home'] == team_name]['division']
        if len(home_division) > 0:
            division = list(home_division)[0]

            # Change keys of players
            player_data = []
            for i, value in enumerate(player):
                if PLAYER_KEYS.issubset(value.keys()):
                    player_data.append({
                        'Name_discord': value['nameDiscord'],
                        'aoe2_id': int(value['aoe2Id'])
                    })

                    # Query aoe2.net for current stats
                    rm_rating, tg_rating = get_player_rating(player_data[i]['aoe2_id'])
                    player_data[i]['crt_rating_rm'] = rm_rating
                    player_data[i]['crt_rating_tg'] = tg_rating

            # Add line
            final_team_df.loc[df_index] = [team_name, player_data, division] 
            df_index += 1
            
    # Format the same names and drop extra columns
    match_df.drop('Matchday', axis=1, inplace=True)
    match_df.drop('set', axis=1, inplace=True)
    match_df.drop('startDate', axis=1, inplace=True)
    match_df.drop('captain', axis=1, inplace=True)
    match_df.drop('game', axis=1, inplace=True)
    match_df.drop('map', axis=1, inplace=True)
    match_df.drop('submitted_by', axis=1, inplace=True)
    match_df.drop('submit_date', axis=1, inplace=True)
    match_df.drop('submitted', axis=1, inplace=True)
    match_df.rename(columns={'winner': 'Winner', 'loser': 'Loser', 'game_id': 'Game ID', 'division': 'Division'}, inplace=True)

    return final_team_df, match_df

def get_aoe_data(season: int):
    # Connect to DB
    client = database_connect()

    if season == 4:
        # Get data from db but from old structure
        team_df, match_df = get_aoe_league_data_depreciated(client)
    else:
        # Get data from db from current structure
        team_df, match_df = get_aoe_league_data(client)

    # Close DB Connection
    client.close()

    return team_df, match_df