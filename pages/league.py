import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table

from app import app
import data_store

# Create bar chart types and traces
graph_types = ['Map', 'Civilization']

# Create layout
layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H5('League Records')),
        ]),
        dbc.Row([
            dbc.Col(html.P(
                'Overall statistics across all division within the League of Empires Season 5. Game distribution can be set to Map or Civilization and will show the games played or games won/lost respectively.'
            )),
        ]),
        dbc.Row([
            dbc.Col(html.P('Game Distribution by: '), width="auto"),
            dbc.Col(dcc.Dropdown(
                    id='league-graph-type',
                    options=[{'label': i, 'value': i} for i in graph_types],
                    value=graph_types[0]
            ), width=4)
        ], style={"padding-bottom": "15px"}),
        dbc.Row([ 
            dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(
                        id='league-graph'
                    ))
                ]),
            ])
        ]),
        dbc.Row([
            dbc.Col(html.P(
                'Additionally, a conditional distribution can be visualized by selecting one map or civilization. For example, if Map is selected above then Arabia can be selected to see the win/loss distribution by civilization on Arabia.'
            ))
        ]),
        dbc.Row([
            dbc.Col(html.P('Conditional Game Distribution by: '), width="auto"),
            dbc.Col(dcc.Dropdown(
                    id='league-sub-graph-type'
            ), width=4)
        ], style={"padding-bottom": "15px"}),
        dbc.Row([ 
            dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(
                        id='league-sub-graph'
                    ))
                ]),
            ])
        ]),
    ])
])

@app.callback(
    [Output('league-graph', 'figure'), Output('league-sub-graph-type', 'options'), Output('league-sub-graph-type', 'value')],
    [Input('league-graph-type', 'value'), Input('season-selection', 'value')])
def update_graph(selected_type, season_num):
    # Aggregate data
    if selected_type == 'Map':
        reduced_league_df = data_store.team_game_info_df[season_num].groupby(['Map', 'Type']).agg({'Count': 'sum'}).reset_index()

        # Create sub graph type list
        sub_graph_types = reduced_league_df['Map'].unique()
    else:
        reduced_league_df = data_store.team_game_info_df[season_num].groupby(['Civilization', 'Type']).agg({'Count':'sum'}).reset_index()

        # Create sub graph type list
        sub_graph_types = reduced_league_df['Civilization'].unique()

    # Create subgraph options and value
    sub_graph_options = [{'label': i, 'value': i} for i in sub_graph_types]
    sub_graph_value = sub_graph_types[0]

    # Create traces
    lost_trace = reduced_league_df[reduced_league_df['Type'] == 'Games Lost']
    win_trace = reduced_league_df[reduced_league_df['Type'] == 'Games Won']

    # Create bar chart
    if selected_type == 'Map':
        games_played_data = win_trace['Count'] / 3.0
        fig = go.Figure(data=[
            go.Bar(
                x=lost_trace[selected_type],
                y=games_played_data,
                name='Games Played'
            )
        ])
    else:
        fig = go.Figure(data=[
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
    fig.update_layout(barmode='stack')

    return fig, sub_graph_options, sub_graph_value

@app.callback(
    Output('league-sub-graph', 'figure'),
    [Input('league-graph-type', 'value'), Input('league-sub-graph-type', 'value'), Input('season-selection', 'value')])
def update_sub_graph(selected_type, sub_selected_type, season_num):
    # Assign flipped variables
    if selected_type == 'Map':
        sub_graph_label_name = 'Civilization'
    else:
        sub_graph_label_name = 'Map'

    # Aggregate sub data
    sub_graph_league_df = data_store.team_game_info_df[season_num][data_store.team_game_info_df[season_num][selected_type] == sub_selected_type]
    sub_graph_league_df = sub_graph_league_df.groupby([sub_graph_label_name, 'Type']).agg({'Count': 'sum'}).reset_index()

    # Create traces
    sub_lost_trace = sub_graph_league_df[sub_graph_league_df['Type'] == 'Games Lost']
    sub_win_trace = sub_graph_league_df[sub_graph_league_df['Type'] == 'Games Won']

    # Create sub graph bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=sub_lost_trace[sub_graph_label_name],
            y=sub_lost_trace['Count'],
            name='Games Lost'
        ),
        go.Bar(
            x=sub_win_trace[sub_graph_label_name],
            y=sub_win_trace['Count'],
            name='Games Won'
        )
    ])
    fig.update_layout(barmode='stack')

    return fig  