import pandas as pd
import boto
import os
import shutil
import json

# Constants
DEBUG = False
SEASONS = [4,5]

# Data store contents
team_df = {}
match_df = {}
division_df = {}
team_game_count_df = {}
team_game_info_df = {}

# DIRECOTRY NAME
DIR_NAME = 'temp_season_data'

def download_s3_data_file(league_bucket, season_num, file_name):
    # If folder doesn't exist, then create it.
    if not os.path.isdir('{}/season_{}'.format(DIR_NAME, season_num)):
        os.makedirs('{}/season_{}'.format(DIR_NAME, season_num))

    # Get file
    team_df_key = league_bucket.get_key('data_views/season_{}/{}.pkl'.format(season_num, file_name))
    with open('{}/season_{}/{}.pkl'.format(DIR_NAME, season_num, file_name), 'wb') as team_df_file:
        team_df_key.get_file(team_df_file)

def load_data_store():
    global team_df, match_df, division_df, team_game_count_df, team_game_info_df
    
    if not DEBUG:
        # Read files with credentials
        with open('db_conn.json') as json_file:
            db_conn_json = json.load(json_file)

        # Connect to S3
        conn = boto.s3.connect_to_region(
            'us-east-2',
            aws_access_key_id=db_conn_json['aws-access-key-id'],
            aws_secret_access_key=db_conn_json['aws-secret-access-key'],
            is_secure=True
        )
        league_bucket = conn.get_bucket(db_conn_json['aws-bucket-name'])

        # Clear folder and create new
        if os.path.isdir(DIR_NAME):
            shutil.rmtree(DIR_NAME)
            os.makedirs(DIR_NAME)

        # Downlaod files for season 4 and 5
        for season in SEASONS:
            download_s3_data_file(league_bucket, season, 'team_df')
            download_s3_data_file(league_bucket, season, 'match_df')
            download_s3_data_file(league_bucket, season, 'division_df')
            download_s3_data_file(league_bucket, season, 'team_game_count_df')
            download_s3_data_file(league_bucket, season, 'team_game_info_df')

    # Read various data frames from file
    for season in SEASONS:
        team_df[season] = pd.read_pickle('{}/season_{}/team_df.pkl'.format(DIR_NAME, season))
        match_df[season] = pd.read_pickle('{}/season_{}/match_df.pkl'.format(DIR_NAME, season))
        division_df[season] = pd.read_pickle('{}/season_{}/division_df.pkl'.format(DIR_NAME, season))
        team_game_count_df[season] = pd.read_pickle('{}/season_{}/team_game_count_df.pkl'.format(DIR_NAME, season))
        team_game_info_df[season] = pd.read_pickle('{}/season_{}/team_game_info_df.pkl'.format(DIR_NAME, season))

    