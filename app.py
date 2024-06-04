import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

data = pd.read_csv('combined_airquality_edit.csv')
data = pd.read_csv('combined_airquality_edit.csv')
data['City/Town/Village/Area'] = data['City/Town/Village/Area'].replace({
    'Kotttayam': 'Kottayam',
    'Trivendrum': 'Trivandrum',
    'Kochi': 'Cochin',
    'Thiruvananthapuram': 'Trivandrum'
})

# List of cities for the dropdown
cities = data['City/Town/Village/Area'].unique()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='city-dropdown',
                options=[{'label': city, 'value': city} for city in cities],
                value=['Palakkad'],
                multi=True
            ),
            dcc.Graph(id='no2-graph'),
            dcc.Graph(id='rspm-pm10-graph'),
            dcc.Graph(id='so2-graph')
        ], width=8),
        dbc.Col([
            html.Div([
                html.H4("Data Source"),
                html.P("These data were obtained from www.kerala.data.gov for the years 1987 to 2015. "
                       "Some of the years in between were not available. The datasets were "
                       "concatenated and cleaned for visualization clarity. You can use the dropdown bar to filter for different cities."),
                       html.Br(),
                       html.P("The graphs currently look slightly chaotic as the values have not been treated for yearly averaged readings."
                              "Hover over the lines to interactively track the dates. As the reported dates varied in formats, there may have been misinterpretation errors when preparing the data."),
                       html.Br(),
                       html.P("This page should be used as a proof-of-concept demo and if further analysis is required, data quality would need to be further improved."
                              " Data is filtered for year 2000 onwards due to inconsistent data reporting in earlier years.")    
        ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'background-color': '#f9f9f9'})
        ], width=4, style={'padding': '20px'})
    ])
])

@app.callback(
    [Output('no2-graph', 'figure'),
     Output('rspm-pm10-graph', 'figure'),
     Output('so2-graph', 'figure')],
    [Input('city-dropdown', 'value')]
)
def update_graphs(selected_cities):
    filtered_data = data[data['City/Town/Village/Area'].isin(selected_cities)]
    if filtered_data.empty:
        return (
            {'data': [], 'layout': {'title': 'No Data Available'}},
            {'data': [], 'layout': {'title': 'No Data Available'}},
            {'data': [], 'layout': {'title': 'No Data Available'}}
        )

    no2_traces = []
    rspm_pm10_traces = []
    so2_traces = []

    for city in selected_cities:
        city_data = filtered_data[filtered_data['City/Town/Village/Area'] == city]
        city_data['Date'] = pd.to_datetime(city_data[['Year', 'Month']].assign(DAY=1))
        city_data = city_data[city_data['Date'].dt.year >= 2000]
        city_data.set_index('Date', inplace=True)

        # Convert object columns to appropriate types
        city_data = city_data.infer_objects()
        
        city_data = city_data.interpolate(method='time')

        no2_traces.append({
            'x': city_data.index,
            'y': city_data['NO2'],
            'type': 'line',
            'name': f'{city} NO2'
        })
        rspm_pm10_traces.append({
            'x': city_data.index,
            'y': city_data['RSPM/PM10'],
            'type': 'line',
            'name': f'{city} PM10'
        })
        so2_traces.append({
            'x': city_data.index,
            'y': city_data['SO2'],
            'type': 'line',
            'name': f'{city} SO2'
        })

    no2_figure = {
        'data': no2_traces,
        'layout': {
            'title': f'Air Quality of {selected_cities[0]} - NO2 Levels',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Concentration of NO2'}
        }
    }

    rspm_pm10_figure = {
        'data': rspm_pm10_traces,
        'layout': {
            'title': f'Air Quality of {selected_cities[0]} - PM10 Levels',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Concentration of PM10'}
        }
    }

    so2_figure = {
        'data': so2_traces,
        'layout': {
            'title': f'Air Quality of {selected_cities[0]} - SO2 Levels',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Concentration of SO2'}
        }
    }

    return no2_figure, rspm_pm10_figure, so2_figure

if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=True, port=8051)