import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px

from app import app
import data_store

# Create layout
layout = html.Div(children=[
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H4(children='Player statistics are under construction. Check back later.'))
        ])
    ])
])