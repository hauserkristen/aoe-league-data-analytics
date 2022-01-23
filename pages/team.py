import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table
import pandas as pd

from app import app
import data_store

# Get all team names
team_names = data_store.team_df[max(data_store.SEASONS)]['Team Name']

# Format and downselect table data
COLUMN_NAMES = ['Discord Name', 'AoE 2 ID', 'Current RM Rating', 'Current TG RM Rating']
PLAYER_DESC_KEYS = ['Name_discord', 'aoe2_id']
column_labels = [{'name': i, 'id': i} for i in COLUMN_NAMES]

# Create bar chart types and traces
graph_types = ['Map', 'Civilization']

# Create card content
card_won_content = [
    dbc.CardHeader('Games Won'),
    dbc.CardBody(id='games-won'),
]

card_loss_content = [
    dbc.CardHeader('Games Lost'),
    dbc.CardBody(id='games-lost'),
]

card_played_content = [
    dbc.CardHeader('Games Played'),
    dbc.CardBody(id='games-played'),
]

# Create layout
layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H5('Team Records')),
        ]),
        dbc.Row([
            dbc.Col(html.P(
                'Statistics for a single team within the League of Empires Season 5. The table below summarizes the team and then the graph below that summarizes how many games each player has been won/lost. It is important to note that if the aoe2.net ID registered with did not match the in game ID, records may not have been recorded properly.'
            )),
        ]),
        dbc.Row([
            dbc.Col(html.P('Team Name: '), width='auto'),
            dbc.Col(dcc.Dropdown(
                    id='team-selection',
                    options=[{'label': i, 'value': i} for i in team_names],
                    value = team_names[0]
            ), width=4)
        ], style={'padding-bottom': '15px'}),
        dbc.Row([
            dbc.Col(dbc.Card(card_played_content, color='primary', outline=True),),
            dbc.Col(dbc.Card(card_won_content, color='primary', outline=True),),
            dbc.Col(dbc.Card(card_loss_content, color='primary', outline=True),)
        ], style={'padding-bottom': '15px'}),
        dbc.Row([ 
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.H5('Team Description')),
                ]),
                dbc.Row([
                    dbc.Col(dash_table.DataTable(
                        id='team-desc-table',
                        columns=column_labels
                    ), style={'padding-bottom': '15px'}),
                ]),
                dbc.Row([
                    dbc.Col(html.H5('Number of games played and won by each player.')),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(
                        id='team-count-graph'
                    ))
                ]),
            ])
        ]),
        dbc.Row([
            dbc.Col(html.P(
                'Game distribution can be set to Map or Civilization and will show the games won/lost by this team.'
            )),
        ]),
        dbc.Row([
            dbc.Col(html.P('Game Distribution by: '), width='auto'),
            dbc.Col(dcc.Dropdown(
                    id='team-graph-type',
                    options=[{'label': i, 'value': i} for i in graph_types],
                    value=graph_types[0]
            ), width=4)
        ], style={'padding-bottom': '15px'}),
        dbc.Row([ 
            dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(
                        id='team-graph'
                    ))
                ]),
            ])
        ]),
    ])
])

@app.callback(
    [Output('team-count-graph', 'figure'), Output('team-desc-table', 'data'), Output('games-played', 'children'), Output('games-won', 'children'), Output('games-lost', 'children')],
    [Input('team-selection', 'value'), Input('season-selection', 'value')])
def update_game_count_graph(selected_team_name, season_num):
    # Get data
    selected_team_game_count_df = data_store.team_game_count_df[season_num][data_store.team_game_count_df[season_num]['Team Name'] == selected_team_name]

    # Seperate into traces
    play_trace = selected_team_game_count_df[selected_team_game_count_df['Type'] == 'Games Lost']
    win_trace = selected_team_game_count_df[selected_team_game_count_df['Type'] == 'Games Won']

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=play_trace['Player Name'],
            y=play_trace['Count'],
            name='Games Lost'
        ),
        go.Bar(
            x=win_trace['Player Name'],
            y=win_trace['Count'],
            name='Games Won'
        ),
    ])
    fig.update_layout(barmode='stack')

    # Get team description
    table_data = data_store.team_df[season_num][data_store.team_df[season_num]['Team Name'] == selected_team_name]
    table_data = list(table_data['Player'])[0]

    # Format and downselect table data
    table_df = pd.DataFrame(columns=COLUMN_NAMES)
    for i, player_data in enumerate(table_data):
        if all([key in player_data.keys() for key in PLAYER_DESC_KEYS]):
            # Get keys that are available
            if 'crt_rating_rm' not in player_data.keys():
                rm_rating = 'N/A'
            else:
                rm_rating = player_data['crt_rating_rm']
            if 'crt_rating_tg' not in player_data.keys():
                tg_rating = 'N/A'
            else:
                tg_rating = player_data['crt_rating_tg']

            table_df.loc[i] = [player_data['Name_discord'], player_data['aoe2_id'], rm_rating, tg_rating]

    # Create badge data
    selected_team_div_df = data_store.division_df[season_num][data_store.division_df[season_num]['Team Name'] == selected_team_name]
    games_played = html.H5('{}'.format(selected_team_div_df['Games Played'].item()), className='card-title')
    games_won = html.H5('{}'.format(selected_team_div_df['Games Won'].item()), className='card-title')
    games_lost = html.H5('{}'.format(selected_team_div_df['Games Lost'].item()), className='card-title')
    
    return fig, table_df.to_dict('records'), games_played, games_won, games_lost

@app.callback(
    Output('team-graph', 'figure'),
    [Input('team-selection', 'value'), Input('team-graph-type', 'value'), Input('season-selection', 'value')])
def update_game_graph(selected_team_name, selected_type, season_num):
    # Get team game info
    selected_team_game_info_df = data_store.team_game_info_df[season_num][data_store.team_game_info_df[season_num]['Team Name'] == selected_team_name]

    if selected_type == 'Map':
        reduced_team_df = selected_team_game_info_df.groupby(['Map', 'Type']).agg({'Count': 'sum'}).reset_index()
    else:
        reduced_team_df = selected_team_game_info_df.groupby(['Civilization', 'Type']).agg({'Count':'sum'}).reset_index()

    # Create traces
    lost_trace = reduced_team_df[reduced_team_df['Type'] == 'Games Lost']
    win_trace = reduced_team_df[reduced_team_df['Type'] == 'Games Won']

    # Create bar chart
    if selected_type == 'Map':
        game_fig = go.Figure(data=[
            go.Bar(
                x=lost_trace[selected_type],
                y=lost_trace['Count'] / 3.0,
                name='Games Lost'
            ),
            go.Bar(
                x=win_trace[selected_type],
                y=win_trace['Count'] / 3.0,
                name='Games Won'
            ),
        ])
    else:
        game_fig = go.Figure(data=[
            go.Bar(
                x=lost_trace[selected_type],
                y=lost_trace['Count'],
                name='Games Lost'
            ),
            go.Bar(
                x=win_trace[selected_type],
                y=win_trace['Count'],
                name='Games Won'
            ),
        ])
    game_fig.update_layout(barmode='stack')

    return game_fig

