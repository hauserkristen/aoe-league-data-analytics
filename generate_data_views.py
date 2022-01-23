import pandas as pd
import os
import argparse

from data_views.db_connect import get_aoe_data
from data_views import get_division_data, get_team_data

def main():
    parser = argparse.ArgumentParser(description='Define the AoE league season number as int.')
    parser.add_argument('season', type=int, help='Integer season number.')
    args = parser.parse_args()

    # Get data from DB and convert to pandas data frames
    team_df, match_df = get_aoe_data(args.season)
    match_df = match_df.dropna()
    team_df.to_pickle('data_frames\\season_{}\\team_df.pkl'.format(args.season))
    match_df.to_pickle('data_frames\\season_{}\\match_df.pkl'.format(args.season))
    print('Team and Match data read...')

    # Get division data
    division_df = get_division_data(team_df, match_df)
    division_df.to_pickle('data_frames\\season_{}\\division_df.pkl'.format(args.season))
    print('Division data read...')

    # Get team data for each team
    team_names = team_df['Team Name']
    if os.path.isfile('data_frames\\team_game_count_df.pkl') and os.path.isfile('data_frames\\season_{}\\team_game_info_df.pkl'.format(args.season)):
        team_game_count_df = pd.read_pickle('data_frames\\season_{}\\team_game_count_df.pkl'.format(args.season))
        team_game_info_df = pd.read_pickle('data_frames\\season_{}\\team_game_count_df.pkl'.format(args.season))

        # Remove previously processed teams
        processed_team_names = team_game_count_df['Team Name']
        processed_team_names = processed_team_names.drop_duplicates()
        team_name_indicator = team_names.isin(processed_team_names)
        team_names = team_names[~team_name_indicator]
    else:
        team_game_count_df = pd.DataFrame(columns=[
            'Team Name',
            'Player Name',
            'Count',
            'Type'
        ])

        team_game_info_df = pd.DataFrame(columns=[
            'Team Name',
            'Civilization',
            'Map',
            'Count',
            'Type'
        ])

    for team in team_names:
        # Get data
        selected_team_game_count_df, selected_team_game_info_df = get_team_data(team, team_df, match_df)

        # Aggregate data frames
        team_game_count_df = team_game_count_df.append(selected_team_game_count_df, ignore_index=True)
        team_game_info_df = team_game_info_df.append(selected_team_game_info_df, ignore_index=True)

        # Save
        team_game_count_df.to_pickle('data_frames\\season_{}\\team_game_count_df.pkl'.format(args.season))
        team_game_info_df.to_pickle('data_frames\\season_{}\\team_game_info_df.pkl'.format(args.season))

    print('Complete...')

if __name__ == '__main__':
    main()