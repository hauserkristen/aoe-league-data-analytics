import requests
import pandas as pd
import json

from .data_retrieval import get_cached_match_ids, get_match_info

def get_team_data(team_name, team_df, match_df):
    # Create dataframe
    team_game_count_df = pd.DataFrame(columns=[
        'Team Name',
        'Player Name',
        'Count',
        'Type'
    ])
    team_game_count_df_index = 0

    team_game_df = pd.DataFrame(columns=[
        'Team Name',
        'Civilization',
        'Map',
        'Count',
        'Type'
    ])
    team_game_df_index = 0

    # Get team AoE2.net IDs
    team_info = team_df[team_df['Team Name'] == team_name]

    # Create name map in case names match
    team_aoe2_ids = []
    aoe2_id_name_map = {}
    
    # Record aoe2 IDs and names
    for teammate in list(team_info['Player'])[0]:
        if 'aoe2_id' in teammate.keys():
            team_aoe2_ids.append(str(teammate['aoe2_id']))

            # Format to match steam names
            teammate_name = teammate['Name_discord']
            teammate_name = teammate_name[:teammate_name.find('#')].strip()

            # Record map
            aoe2_id_name_map[teammate_name] = str(teammate['aoe2_id'])

    
    # Record how many games each teammate played
    lost_count = {id:0 for id in team_aoe2_ids}
    win_count = {id:0 for id in team_aoe2_ids}

    # Record how many games were played for each map civ
    team_lost_count = {}
    team_win_count = {}

    # Query string constants
    QUERY_STRING = 'https://aoe2.net/api/strings?game=aoe2de&language=en'
    response = requests.get(QUERY_STRING)
    string_info = response.json()

    # Create Civ Map
    CIV_MAP = {civ_info['id']:civ_info['string'] for civ_info in string_info['civ']}

    # Create Map Map
    MAP_MAP = {map_info['id']:map_info['string'] for map_info in string_info['map_type']}

    # Identify matches for this team
    team_home_matches = match_df[match_df['Home'] == team_name]
    team_away_matches = match_df[match_df['Away'] == team_name]
    team_matches = pd.concat([team_home_matches, team_away_matches])

    # Get match IDs in data cache
    cached_match_ids = get_cached_match_ids()

    # Loop through each match
    if not team_matches.empty:
        for winning_team, losing_team, match_id in zip(team_matches['Winner'], team_matches['Loser'], team_matches['Game ID']):
            # Record team stats
            search_team_won = None
            if team_name == winning_team:
                search_team_won = True
            if team_name == losing_team:
                search_team_won = False

            if search_team_won is not None:
                successful_retrieval, match_info = get_match_info(match_id, cached_match_ids)
                        
                # Process if successful data retrieval
                if successful_retrieval:

                    # Get map and identify name
                    map = int(match_info['map_type'])
                    map_name = MAP_MAP[map]

                    # Record teammate activites
                    for player in match_info['players']:
                        player_id = str(player['profile_id'])
                        player_name = str(player['name'])
                        player_won = player['won']

                        # Get civ and identify name
                        civ = int(player['civ'])
                        civ_name = CIV_MAP[civ]

                        # Add to dictionary if not currently in there
                        if (player_won and search_team_won) or (not player_won and not search_team_won):
                            if civ_name not in team_lost_count.keys():
                                team_lost_count[civ_name] = {}
                                team_win_count[civ_name] = {}
                            if map_name not in team_lost_count[civ_name].keys():
                                team_lost_count[civ_name][map_name] = 0
                                team_win_count[civ_name][map_name] = 0

                            # Record wins and loses
                            if player_won:
                                team_win_count[civ_name][map_name]  += 1
                            else:
                                team_lost_count[civ_name][map_name] += 1

                        if not player_won and player_id in win_count.keys():
                            lost_count[player_id] += 1
                        elif not player_won and player_name in aoe2_id_name_map.keys():
                            lost_count[aoe2_id_name_map[player_name]] += 1

                        if player_won and player_id in win_count.keys():
                            win_count[player_id] += 1
                        elif player_won and player_name in aoe2_id_name_map.keys():
                            lost_count[aoe2_id_name_map[player_name]] += 1
        
        # Add to data frame
        for aoe2_id in team_aoe2_ids:
            # Get player name
            player_name = list(aoe2_id_name_map.keys())[list(aoe2_id_name_map.values()).index(aoe2_id)]

            # Add row for game count
            team_game_count_df.loc[team_game_count_df_index] = [team_name, player_name, lost_count[aoe2_id], 'Games Lost']
            team_game_count_df_index += 1

            # Add row for win count
            team_game_count_df.loc[team_game_count_df_index] = [team_name, player_name, win_count[aoe2_id], 'Games Won']
            team_game_count_df_index += 1

        for civ_name in team_lost_count.keys():
            for map_name in team_lost_count[civ_name].keys():
                # Add row for game count
                team_game_df.loc[team_game_df_index] = [team_name, civ_name, map_name, team_lost_count[civ_name][map_name], 'Games Lost']
                team_game_df_index += 1

                # Add row for win count
                team_game_df.loc[team_game_df_index] = [team_name, civ_name, map_name, team_win_count[civ_name][map_name], 'Games Won']
                team_game_df_index += 1
    

    return team_game_count_df, team_game_df