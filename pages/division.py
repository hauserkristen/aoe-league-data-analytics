import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table

from app import app
import data_store

# Create division names
divisions = {div:'Division {}'.format(int(div)) for div in data_store.division_df[max(data_store.SEASONS)]['Division']}

# Set up initial table data
division_nums = list(divisions.keys())
division_nums.sort()
initial_division = division_nums[0]
initial_league_table_data = data_store.division_df[max(data_store.SEASONS)][data_store.division_df[max(data_store.SEASONS)]['Division'] == initial_division]
initial_league_table_data = initial_league_table_data.sort_values(by=['Games Won'], ascending=False).to_dict('records')
column_labels = [{'name': i, 'id': i} for i in data_store.division_df[max(data_store.SEASONS)].columns if i != 'Division']

# Create bar chart types and traces
graph_types = ['Map', 'Civilization']

# Create layout
layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.H5('Division Records')),
                ]),
                dbc.Row([
                    dbc.Col(html.P(
                        'Statistics across a single division within the League of Empires Season 5. The table below summarizes the season\'s progress thus far.'
                    )),
                ]),
                dbc.Row([
                    dbc.Col(html.P('Division: '), width="auto"),
                    dbc.Col(dcc.Dropdown(
                            id='div-selection',
                            options=[{'label': name, 'value': id} for id, name in divisions.items()],
                            value=initial_division
                    ), width=4)
                ], style={"padding-bottom": "15px"}),
                dbc.Row([ 
                    dbc.Container([
                        dbc.Row([
                            dbc.Col(dash_table.DataTable(
                                id='div-table',
                                data=initial_league_table_data,
                                columns=column_labels
                            ), style={"padding-bottom": "25px"}),
                        ]),
                    ])
                ]), 
            ])
        ]),
        dbc.Row([
            dbc.Col(html.P(
                'Game distribution can be set to Map or Civilization and will show the games played or games won/lost respectively within this division.'
            )),
        ]),
        dbc.Row([
            dbc.Col(html.P('Game Distribution by: '), width="auto"),
            dbc.Col(dcc.Dropdown(
                    id='division-graph-type',
                    options=[{'label': i, 'value': i} for i in graph_types],
                    value=graph_types[0]
            ), width=4)
        ], style={"padding-bottom": "15px"}),
        dbc.Row([ 
            dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(
                        id='division-graph'
                    ))
                ]),
            ])
        ]),
        dbc.Row([
            dbc.Col(html.P(
                'As with the league statistics page, a conditional distribution can be visualized by selecting one map or civilization for this division. For example, if Map is selected above then Arabia can be selected to see the win/loss distribution by civilization on Arabia.'
            ))
        ]),
        dbc.Row([
            dbc.Col(html.P('Conditional Game Distribution by: '), width="auto"),
            dbc.Col(dcc.Dropdown(
                    id='division-sub-graph-type'
            ), width=4)
        ], style={"padding-bottom": "15px"}),
        dbc.Row([ 
            dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(
                        id='division-sub-graph'
                    ))
                ]),
            ])
        ]),
    ])
])

@app.callback(
    Output('div-table', 'data'),
    [Input('div-selection', 'value'), Input('season-selection', 'value')])
def update_table(selected_division, season_num):
    table_data = data_store.division_df[season_num][data_store.division_df[season_num]['Division'] == selected_division]
    table_data = table_data.sort_values(by=['Games Won'], ascending=False)
    return table_data.to_dict('records')

@app.callback(
    [Output('division-graph', 'figure'), Output('division-sub-graph-type', 'options'), Output('division-sub-graph-type', 'value')],
    [Input('div-selection', 'value'), Input('division-graph-type', 'value'), Input('season-selection', 'value')])
def update_graph(selected_division, selected_type, season_num):
    # Get team names in division
    division_team_names = data_store.division_df[season_num][data_store.division_df[season_num]['Division'] == selected_division]['Team Name']

    # Downselect by teams
    division_game_info_df = data_store.team_game_info_df[season_num][data_store.team_game_info_df[season_num]['Team Name'].isin(division_team_names)]
    
    # Aggregate data
    if selected_type == 'Map':
        reduced_division_df = division_game_info_df.groupby(['Map', 'Type']).agg({'Count': 'sum'}).reset_index()

        # Create sub graph type list
        sub_graph_types = reduced_division_df['Map'].unique()
    else:
        reduced_division_df = division_game_info_df.groupby(['Civilization', 'Type']).agg({'Count':'sum'}).reset_index()

        # Create sub graph type list
        sub_graph_types = reduced_division_df['Civilization'].unique()

    # Create subgraph options and value
    sub_graph_options = [{'label': i, 'value': i} for i in sub_graph_types]
    sub_graph_value = sub_graph_types[0]

    # Create traces
    lost_trace = reduced_division_df[reduced_division_df['Type'] == 'Games Lost']
    win_trace = reduced_division_df[reduced_division_df['Type'] == 'Games Won']

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
    Output('division-sub-graph', 'figure'),
    [Input('div-selection', 'value'), Input('division-graph-type', 'value'), Input('division-sub-graph-type', 'value'), Input('season-selection', 'value')])
def update_sub_graph(selected_division, selected_type, sub_selected_type, season_num):
    # Assign flipped variables
    if selected_type == 'Map':
        sub_graph_label_name = 'Civilization'
    else:
        sub_graph_label_name = 'Map'

    # Get team names in division
    division_team_names = data_store.division_df[season_num][data_store.division_df[season_num]['Division'] == selected_division]['Team Name']

    # Downselect by teams
    division_game_info_df = data_store.team_game_info_df[season_num][data_store.team_game_info_df[season_num]['Team Name'].isin(division_team_names)]

    # Aggregate sub data
    sub_graph_league_df = division_game_info_df[division_game_info_df[selected_type] == sub_selected_type]
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