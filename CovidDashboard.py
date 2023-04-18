# Importing the necessary packages
import pathlib
import pandas as pd
import plotly.express as px
from pathlib import Path
import dash_bootstrap_components as dbc
from dash import dash, html, dcc, Input, Output, State

# Getting the data into python from downloaded file
main_file_path = pathlib.Path(__file__)
parent_folder = main_file_path.parent
data_file = parent_folder / 'CovidData.csv'
data_file.is_file()
covid_data = pd.read_csv(data_file)
covid_data

# Check to ensure no missing values 
assert not covid_data.index.hasnans

# Create the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
server=app.server

# Container for the elements
app.layout = dbc.Container([
    dbc.Row([
        # Heading, intro, data source
        dbc.Col([
            html.H1("COVID-19 Dashboard", className='text-center mt-3 mb-2'),
            html.P("COVID-19 was a global pandemic that started in 2020 and brought havoc to the United States.  Over the next few years, government agencies monitored the number of cases of COVID-19 and related deaths in each state.  This dashboard displays historical data in order to help better understand the geographical progression and timeline of infection.  On the left, a line graph allows you to compare the number of cases or deaths (you choose) suffered by the states of interest.  On the right, an animated heat map provides a visualization of the progression of infection.", className='mx-5'),
            html.Div([
                html.A('Data Source - The COVID Tracking Project', href = 'https://covidtracking.com/data', className='mx-5'), 
            ],style={'textAlign': 'center'})    
        ])
    ]),
    
    dbc.Row([
        # First graph in a separate column
        dbc.Col([
            html.H3("Cases or Deaths by State", style={'textAlign': 'center'}),
            dcc.Graph(id='line-graph', style={'height': '445px'}),
            html.Div([
                # Dropdown to select states and radioitems for cases or deaths
                html.Label('Select state(s):', style=dict(marginBottom=3)),
                dcc.Dropdown(id='line-dropdown',
                             options=[{'label': state, 'value': state} for state in covid_data['state'].unique()],
                             value=['Illinois'], multi=True),
                html.Br(),
                html.Label('Select data:', style=dict(marginBottom=3)),
                dcc.RadioItems(id='radio-cases-deaths',
                               options=[{'label': 'Cases', 'value': 'cases'},
                                        {'label': 'Deaths', 'value': 'deaths'}],
                               value='cases', 
                               labelStyle={'display': 'inline-block', 'margin-right': '20px'},
                               inputStyle={"margin-right": "5px"})
            ], style={'width': '50%', 'display': 'inline-block'})
        ], width=6),

        # Second graph in a separate column
        dbc.Col([
            html.H3('Map of Cases Over Time', style={'textAlign': 'center'}),
            dcc.Graph(id='map-graph', style={'height': '400px'})
        ], width=6)
    ], justify='center', style={'margin': '20px'})
], fluid=True)


# Define the callback for the line graph
@app.callback(
    Output('line-graph', 'figure'),
    Input('line-dropdown', 'value'),
    Input('radio-cases-deaths', 'value')
)

# What data to use for the graph componenets
def update_line_graph(states, cases_or_deaths):
    filtered_data = covid_data[covid_data['state'].isin(states)]
    fig = px.line(filtered_data, x='date', y=cases_or_deaths, color='state')

    # Making some formatting changes 
    fig.update_layout(
        xaxis=dict(tickformat='%B %Y',nticks=15, tickangle=45, title_text='',showgrid=False),
        yaxis=dict(showgrid=True, gridwidth=1,gridcolor='lightgrey'),
        plot_bgcolor='#f2f2f2',
        legend_title_text = '',
        legend_font_size = 14,
        paper_bgcolor = 'rgba(0,0,0,0)',
        )

    return fig

# Define the callback for the map graph
@app.callback(
    Output('map-graph', 'figure'),
    Input('line-dropdown', 'value')
)

# Getting a list of two-letter state codes to use for the choropleth
def update_map_graph(states):
    state_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
        'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
        'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
        'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
        'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
        'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
        'Wisconsin': 'WI', 'Wyoming': 'WY'
    }

    # Ensuring the data is in the correct format 
    filtered_data = covid_data.copy()
    filtered_data['state'] = filtered_data['state'].map(state_abbrev).fillna(filtered_data['state'])
    filtered_data = filtered_data.loc[filtered_data['state'].isin(state_abbrev.values())]
    filtered_data['date'] = pd.to_datetime(filtered_data['date'])
    filtered_data['cases'] = filtered_data['cases'].astype(float)
    filtered_data['deaths'] = filtered_data['deaths'].astype(float)



    # PLEASE READ
    # Under the choropleth, on top of the slider, it says "animation_frame=" and then whatever date is being displayed
    # It also says "animation_frame=" when you hover over each state on the map to examine values
    # I realize this is "incorrect" or at least unnapealing to look at, but I could not figure out how to fix it
    # PLEASE READ

    fig = px.choropleth(
        filtered_data,
        locations='state',
        color='cases',
        scope="usa",
        locationmode='USA-states',
        animation_frame=filtered_data['date'].dt.strftime('%B %Y'),
        color_continuous_scale="Viridis",
        hover_data={
            'state': True,
            'cases': ':,.0f',
            'deaths': ':,.0f'
        },
        labels={
            'state': 'State',
            'cases': 'Cases',
            'deaths': 'Deaths'
        },
        height=500
    )

    fig.update_traces(
        zmax=10000000,
        zmin=0,
    )

    fig.update_layout(
        sliders=[{"currentvalue" : {"prefix" : " "}}],
        transition=dict(duration=200, easing='cubic-in-out'),
        geo=dict(bgcolor='#f2f2f2', lakecolor='#ffffff'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
