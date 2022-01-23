import dash
import dash_bootstrap_components as dbc
import pandas as pd
import boto
import os

from data_store import load_data_store

# Create app
external_stylesheets = [dbc.themes.LUX]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

# Load data
load_data_store()