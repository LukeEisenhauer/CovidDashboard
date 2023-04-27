# Importing the necessary packages

import pathlib
import pandas as pd
import dash
import plotly.express as px
from pathlib import Path
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, callback

# Getting the data into python from downloaded file

main_file_path = pathlib.Path(__file__)
parent_folder = main_file_path.parent

data_file = parent_folder / 'CovidData.csv'
data_file.is_file()
covid_data = pd.read_csv(data_file)
covid_data

population_file = parent_folder / 'PopulationData.csv'
population_data = pd.read_csv(population_file)
population_data


merged_data = covid_data.merge(population_data, on="state")

# Calculate per capita cases and deaths for each state
merged_data["per_capita_cases"] = merged_data["cases"] / merged_data["population"] 
merged_data["per_capita_deaths"] = merged_data["deaths"] / merged_data["population"]

# Getting state abbreviations for the map graph 

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

filtered_data = merged_data.copy()
filtered_data['state'] = filtered_data['state'].map(state_abbrev).fillna(filtered_data['state'])
filtered_data = filtered_data.loc[filtered_data['state'].isin(state_abbrev.values())]
filtered_data['date'] = pd.to_datetime(filtered_data['date'])
filtered_data['per_capita_cases'] = filtered_data['per_capita_cases'].astype(float)
filtered_data['per_capita_deaths'] = filtered_data['per_capita_deaths'].astype(float)
filtered_data['date_str'] = filtered_data['date'].dt.strftime('%B %Y')
filtered_data

# Creating the choropleth

heatmap = px.choropleth(
    filtered_data,
    locations='state',
    color='per_capita_cases',
    scope="usa",
    locationmode='USA-states',
    animation_frame='date_str',
    color_continuous_scale="Oranges",
    range_color=(0,filtered_data['per_capita_cases'].max()),
    hover_name='state',
    hover_data={
        'per_capita_cases' : False,
        'date_str' : False,
        'state': False,
        'cases': ':,.0f',
        'deaths': ':,.0f'
    },
    labels={
        'state': 'State',
        'cases': 'Cases',
        'deaths': 'Deaths'
    },

    height=700
)

# Changing the formatting

heatmap.update_layout(
    sliders=[{"currentvalue" : {"prefix" : " "}}],
    transition=dict(duration=200, easing='cubic-in-out'),
    geo=dict(bgcolor='#f2f2f2', lakecolor='#ffffff'),
    coloraxis_colorbar = dict(title='Cases Per Resident'),
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        font_family="Arial"
    )
)

# Layout for page 1

layout_1 = html.Div(
    # This is the landing page with a title, introduction, and data source
    children=[
    html.H1("COVID-19 Dashboard", className='text-center m-5'),
            html.P("COVID-19 is a global pandemic that started in 2020 and brought havoc to the United States and world at large.  It is a virus that causes potentially severe respiratory illness and can be deadly.  Although the elderly and those with underlying health conditions are more apt to experience severe symptoms, the virus can be contracted by anyone of any age.  Additionally, those infected can spread the virus simply by dispersing particles through coughing, sneezing, speaking, and even breathing.  The economic and societal impact of this virus is still being realized today.", className='mx-5'),             
            html.P("Over the years following the virus's introduction, government agencies monitored the number of COVID-19 cases and related deaths in each state.  Harnessing this data is critical for understanding the past, as well as preparing for the future.  This dashboard displays historical data in order to help better understand the geographical progression and timeline of infection.  A line graph allows you to compare the number of cases or deaths suffered by the states of interest.  Additionally, the animated heat map provides a visualization of the progression of infection.", className='mx-5'),
            html.Div([
                html.A('Data Source - The COVID Tracking Project', href = 'https://covidtracking.com/data', className='m-5'), 
            ], className='text-center mt-5')
    ]
)

# Layout for page 2

layout_2=html.Div(
    # This is the page with the line graph and associated
    children=[
    html.H1('Total Cases or Deaths by State',  className='text-center mt-5 mb-0'),
    dcc.Graph(id='line-graph', className='mx-5'),
    dbc.Col(
        width=dict(size=6, offset=3),
        children=[
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
                    inputStyle={"margin-right": "5px"},
                    className='mb-5')
        ])
    ]
)

# Layout for page 3

layout_3=html.Div(
    children=[
    # This is the layout for the choropleth map
    html.H1('Heat Map of the United States', className='text-center mt-5 mb-0'),
    dcc.Graph(figure=heatmap, className='mx-5')
    ]
)

# Instantiate the app

app = Dash(__name__, external_stylesheets=[dbc.themes.UNITED], use_pages=True, pages_folder="")
server = app.server

# Register the pages

dash.register_page(
    "first-page",
    path="/",
    layout=layout_1
)
dash.register_page(
    "second-page",
    layout=layout_2
)
dash.register_page(
    "third-page",
    layout=layout_3
)

# Define the app layout 

app.layout = dbc.Container(
    children=[
        # Page navigation
        dbc.NavbarSimple(
            brand='Covid Visualization Project',
            children=[
                dbc.NavItem( dbc.NavLink('Home Page', href='/') ),
                dbc.NavItem( dbc.NavLink('Line Graph', href='/second-page') ),
                dbc.NavItem( dbc.NavLink('Heat Map', href='/third-page') )
            ],
            color='primary',
            dark=True,
        ),
        dash.page_container,
    ],
    fluid=True,
    class_name = 'px-0'
)

# Define the callback for the line graph

@callback(
    Output('line-graph', 'figure'),
    Input('line-dropdown', 'value'),
    Input('radio-cases-deaths', 'value')
)

# What data to use for the graph 

def update_line_graph(states, cases_or_deaths):
    filtered_data = covid_data[covid_data['state'].isin(states)]
    fig = px.line(filtered_data, x='date', y=cases_or_deaths, color='state')

    # Making some formatting changes 

    fig.update_layout(
        xaxis=dict(tickformat='%B %Y',nticks=15, tickangle=45, title_text='',showgrid=False),
        yaxis=dict(showgrid=True, gridwidth=1,gridcolor='lightgrey', title_text=''),
        plot_bgcolor='#f2f2f2',
        legend_title_text = '',
        legend_font_size = 14,
        paper_bgcolor = 'rgba(0,0,0,0)',
        )

    return fig

# Run the app

if __name__ == '__main__':
    app.run_server()
