import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from app import app
import data_store
from pages import player_layout, team_layout, league_layout, division_layout

# Pull server off app
server = app.server

season_dropdown = dcc.Dropdown(
    id='season-selection',
    options=[{'label': 'Season {}'.format(i), 'value': i} for i in [4,5]],
    value = 5
)

# Building the navigation bar
nav_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem('League Stats', href='/league'),
        dbc.DropdownMenuItem('Division Stats', href='/division'),
        dbc.DropdownMenuItem('Team Stats', href='/team'),
        dbc.DropdownMenuItem('Player Stats', href='/player'),
    ],
    nav = True,
    in_navbar = True,
    label = 'Explore',
)

navbar = dbc.Navbar(
    dbc.Container([
        dbc.Col([
            dbc.Row(dbc.NavbarBrand('League of Empires Season Data Analytics', className='ml-2', href='/home')),
            dbc.Row(html.P('Last Updated: 19/10/2021', style={"margin-left": "8px"}))
        ]),
        dbc.Col(
            season_dropdown,
            width = 4
        ),
        dbc.Col([
            dbc.NavbarToggler(id='navbar-toggler2'),
            dbc.Collapse(
                dbc.Nav(
                    [nav_dropdown], 
                    className='ml-auto', 
                    navbar=True
                ),
                id='navbar-collapse2',
                navbar=True
            )
        ])
    ]),
    color='black',
    dark=True,
    className='mb-4',
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f'navbar-collapse{i}', 'is_open'),
        [Input(f'navbar-toggler{i}', 'n_clicks')],
        [State(f'navbar-collapse{i}', 'is_open')],
    )(toggle_navbar_collapse)

# Embedding the navigation bar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'), Input('season-selection', 'value')])
def update_season(path_name, new_season):
    # Refresh the page
    if path_name == '/team':
        return team_layout
    elif path_name == '/player':
        return player_layout
    elif path_name == '/division':
        return division_layout
    else:
        return league_layout

if __name__ == '__main__':
    # Start server
    app.run_server()