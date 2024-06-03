import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

data = pd.read_csv('combined_airquality_edit.csv')
# Standardize city names
data['City/Town/Village/Area'] = data['City/Town/Village/Area'].replace({
    'Kotttayam': 'Kottayam',
    'Trivendrum': 'Trivandrum',
    'Kochi': 'Cochin',
    'Thiruvananthapuram': 'Trivandrum'
})

# Filter the data for Trivandrum
trivandrum_data = data[data['City/Town/Village/Area'] == 'Trivandrum']

trivandrum_data = trivandrum_data[['Stn Code', 'Month', 'Year', 'SO2', 'NO2',
       'RSPM/PM10', 'SPM', 'PM 2.5']]

# Handle missing values in 'Month' and 'Year' columns
trivandrum_data = trivandrum_data.dropna(subset=['Month', 'Year'])

# Convert 'Month' column to numeric, coercing errors to NaN
trivandrum_data['Month'] = pd.to_numeric(trivandrum_data['Month'], errors='coerce')

# Drop rows where 'Month' conversion resulted in NaN
trivandrum_data = trivandrum_data.dropna(subset=['Month'])

# Convert 'Year' column to integers
trivandrum_data['Year'] = trivandrum_data['Year'].astype(int)
trivandrum_data['Month'] = trivandrum_data['Month'].astype(int)

# Create a datetime column from 'Month' and 'Year'
trivandrum_data['Date'] = pd.to_datetime(trivandrum_data[['Year', 'Month']].assign(DAY=1))

# Filter the data for years from 2000 onwards
trivandrum_data = trivandrum_data[trivandrum_data['Date'].dt.year >= 2000]

# Ensure NO2, PM10, and PM2.5 are numeric
trivandrum_data['NO2'] = pd.to_numeric(trivandrum_data['NO2'], errors='coerce')
trivandrum_data['RSPM/PM10'] = pd.to_numeric(trivandrum_data['RSPM/PM10'], errors='coerce')
trivandrum_data['PM 2.5'] = pd.to_numeric(trivandrum_data['PM 2.5'], errors='coerce')

# Interpolating the missing values
trivandrum_data.set_index('Date', inplace=True)
trivandrum_data['NO2'].interpolate(method='time', inplace=True)
trivandrum_data['RSPM/PM10'].interpolate(method='time', inplace=True)
trivandrum_data['PM 2.5'].interpolate(method='time', inplace=True)

# Resampling the data by month
trivandrum_data = trivandrum_data.resample('M').mean()

# Data preprocessing
data['City/Town/Village/Area'] = data['City/Town/Village/Area'].replace({
    'Kotttayam': 'Kottayam',
    'Trivendrum': 'Trivandrum',
    'Kochi': 'Cochin',
    'Thiruvananthapuram': 'Trivandrum'
})

# Filter the data for Trivandrum
trivandrum_data = data[data['City/Town/Village/Area'] == 'Trivandrum']

trivandrum_data = trivandrum_data[['Stn Code', 'Month', 'Year', 'SO2', 'NO2',
       'RSPM/PM10', 'SPM', 'PM 2.5']]

# Handle missing values in 'Month' and 'Year' columns
trivandrum_data = trivandrum_data.dropna(subset=['Month', 'Year'])

# Convert 'Month' column to numeric, coercing errors to NaN
trivandrum_data['Month'] = pd.to_numeric(trivandrum_data['Month'], errors='coerce')

# Drop rows where 'Month' conversion resulted in NaN
trivandrum_data = trivandrum_data.dropna(subset=['Month'])

# Convert 'Year' column to integers
trivandrum_data['Year'] = trivandrum_data['Year'].astype(int)
trivandrum_data['Month'] = trivandrum_data['Month'].astype(int)

# Create a datetime column from 'Month' and 'Year'
trivandrum_data['Date'] = pd.to_datetime(trivandrum_data[['Year', 'Month']].assign(DAY=1))

# Filter the data for years from 2000 onwards
trivandrum_data = trivandrum_data[trivandrum_data['Date'].dt.year >= 2000]

# Ensure NO2, PM10, and PM2.5 are numeric
trivandrum_data['NO2'] = pd.to_numeric(trivandrum_data['NO2'], errors='coerce')
trivandrum_data['RSPM/PM10'] = pd.to_numeric(trivandrum_data['RSPM/PM10'], errors='coerce')
trivandrum_data['SO2'] = pd.to_numeric(trivandrum_data['SO2'], errors='coerce')

# Interpolating the missing values
trivandrum_data.set_index('Date', inplace=True)
trivandrum_data['NO2'].interpolate(method='time', inplace=True)
trivandrum_data['RSPM/PM10'].interpolate(method='time', inplace=True)
trivandrum_data['SO2'].interpolate(method='time', inplace=True)

# Resampling the data by month
trivandrum_data = trivandrum_data.resample('M').mean()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Air Quality Dashboard for Trivandrum"), className="mb-2")
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='no2-plot'), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='pm10-plot'), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='so2-plot'), width=12)
    ]),
])

# Callback to update plots
@app.callback(
    [Output('no2-plot', 'figure'),
     Output('pm10-plot', 'figure'),
     Output('so2-plot', 'figure')],
    [Input('no2-plot', 'id')]
)
def update_plots(n):
    no2_fig = {
        'data': [{'x': trivandrum_data.index, 'y': trivandrum_data['NO2'], 'type': 'line', 'name': 'NO2'}],
        'layout': {'title': 'NO2 Levels in Trivandrum (2000 Onwards)', 'yaxis': {'title': 'NO2'}, 'xaxis': {'title': 'Date'}}
    }

    pm10_fig = {
        'data': [{'x': trivandrum_data.index, 'y': trivandrum_data['RSPM/PM10'], 'type': 'line', 'name': 'PM10'}],
        'layout': {'title': 'PM10 Levels in Trivandrum (2000 Onwards)', 'yaxis': {'title': 'PM10'}, 'xaxis': {'title': 'Date'}}
    }

    pm25_fig = {
        'data': [{'x': trivandrum_data.index, 'y': trivandrum_data['SO2'], 'type': 'line', 'name': 'SO2'}],
        'layout': {'title': 'SO2 Levels in Trivandrum (2000 Onwards)', 'yaxis': {'title': 'SO2'}, 'xaxis': {'title': 'Date'}}
    }

    return no2_fig, pm10_fig, pm25_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)