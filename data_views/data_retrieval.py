import requests
import json
import os
from os.path import isfile, join

def get_cached_match_ids():
    if not os.path.isdir('data_cache'):
        os.makedirs('data_cache')

    only_files = [os.path.splitext(f)[0] for f in os.listdir('data_cache') if isfile(join('data_cache', f))]

    return only_files


def get_match_info(match_id, cached_match_ids):
    match_info = None

    if not os.path.isdir('data_cache'):
        os.makedirs('data_cache')

    # Check data cache
    if match_id in cached_match_ids:
        # Read from file
        try:
            with open('data_cache/{}.json'.format(match_id), 'w') as file_cache:
                match_info = json.load(file_cache)

            return True, match_info
        except:
            # Delete file and proceed with aoe2.net query
            os.remove('data_cache/{}.json'.format(match_id))

    # aoe2.net query
    QUERY_STRING = 'https://aoe2.net/api/match?match_id={}'.format(match_id)
    retries = 0
    success = False
    while not success and retries < 10:
        try:
            response = requests.get(QUERY_STRING)
            success = True
        except (ConnectionError, TimeoutError):
            retries += 1
            successful_retrieval = False
    
    # Check for success
    successful_retrieval = response.status_code == 200

    # Get data
    if successful_retrieval:
        match_info = response.json()

        # Write data to cache
        with open('data_cache/{}.json'.format(match_id), 'w') as file_cache:
            json.dump(match_info, file_cache)
            
    return successful_retrieval, match_info

def get_player_rating(player_id):
    # aoe2.net query
    RM_QUERY_STRING = 'https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=3&profile_id={}&count=1'.format(player_id)
    retries = 0
    success = False
    while not success and retries < 10:
        try:
            response = requests.get(RM_QUERY_STRING)
            success = True
        except (ConnectionError, TimeoutError):
            retries += 1
            successful_retrieval = False
    
    # Check for success
    successful_retrieval = response.status_code == 200

    # Get data
    if successful_retrieval:
        player_info = response.json()
        if len(player_info) > 0:
            rm_rating = player_info[0]['rating']
        else:
            rm_rating = 'Not Available'
    else:
        rm_rating = 'Not Available'

    # aoe2.net query
    TG_QUERY_STRING = 'https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=4&profile_id={}&count=1'.format(player_id)
    retries = 0
    success = False
    while not success and retries < 10:
        try:
            response = requests.get(TG_QUERY_STRING)
            success = True
        except (ConnectionError, TimeoutError):
            retries += 1
            successful_retrieval = False
    
    # Check for success
    successful_retrieval = response.status_code == 200

    # Get data
    if successful_retrieval:
        player_info = response.json()
        if len(player_info) > 0:
            tg_rating = player_info[0]['rating']
        else:
            tg_rating = 'Not Available'
    else:
        tg_rating = 'Not Available'
            
    return rm_rating, tg_rating