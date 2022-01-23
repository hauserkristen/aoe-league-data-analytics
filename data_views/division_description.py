import pandas as pd

def get_division_data(team_df, match_df):
    # Create division dataframe
    division_df = pd.DataFrame(columns=[
        'Division',
        'Team Name',
        'Games Won',
        'Games Lost',
        'Games Played'
    ])
    division_df_index = 0

    # Record games/wins for each team
    division_lost_count = {}
    division_win_count = {}
    for division, team_name in zip(team_df['Division'], team_df['Team Name']):
        if division not in division_lost_count.keys():
            division_lost_count[division] = {}
            division_win_count[division] = {}

        division_lost_count[division][team_name] = 0
        division_win_count[division][team_name] = 0

    # Loop through all matches
    for division, home_team, away_team, winning_team, losing_team in zip(match_df['Division'], match_df['Home'], match_df['Away'], match_df['Winner'], match_df['Loser']):
        # Record team stats
        if winning_team == home_team or winning_team == away_team:
            division_win_count[division][winning_team] += 1
        if losing_team == home_team or losing_team == away_team:
            division_lost_count[division][losing_team] += 1

    for division in division_lost_count.keys():
        for team_name in division_lost_count[division].keys():
            # Add row for game count
            division_df.loc[division_df_index] = [division, team_name, division_win_count[division][team_name], division_lost_count[division][team_name], division_win_count[division][team_name] + division_lost_count[division][team_name]]
            division_df_index += 1

    return division_df