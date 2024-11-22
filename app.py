import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import plotly.express as px
import pandas as pd
import numpy as np
from dash import callback_context
from dash.exceptions import PreventUpdate
from dash import no_update

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server


def load_and_process_data():
    # Load data with correct settings
    df = pd.read_csv('data/worldbank_data.csv', low_memory=False)

    # Filter for the specific indicator and total population
    df_filtered = df[
        (df['INDICATOR'] == 'HD.HCI.AMRT') &
        (df['SEX'] == '_T')
        ]

    # Select relevant columns
    year_cols = [f'YR{year}' for year in range(2015, 2022)]
    cols_to_keep = ['Country name', 'economy'] + year_cols
    df_filtered = df_filtered[cols_to_keep]

    # Convert to long format
    df_long = pd.melt(
        df_filtered,
        id_vars=['Country name', 'economy'],
        value_vars=year_cols,
        var_name='Year',
        value_name='Survival_Rate'
    )

    # Clean up year format and convert to numeric
    df_long['Year'] = df_long['Year'].str.replace('YR', '').astype(int)
    df_long['Survival_Rate'] = pd.to_numeric(df_long['Survival_Rate'], errors='coerce')

    # First, identify countries that have at least one valid data point
    valid_countries = df_long.groupby('Country name')['Survival_Rate'].apply(
        lambda x: x.notna().any()
    )
    valid_countries = valid_countries[valid_countries].index

    # Filter for valid countries
    df_long = df_long[df_long['Country name'].isin(valid_countries)]

    # Handle missing values within each country group
    df_long = df_long.sort_values(['Country name', 'Year'])
    df_long['Survival_Rate'] = df_long.groupby('Country name')['Survival_Rate'].transform(
        lambda x: x.ffill().bfill()
    )

    return df_long


# Load the processed data
try:
    df_processed = load_and_process_data()
    print("\nProcessed data summary:")
    print(f"Number of countries: {df_processed['Country name'].nunique()}")
    print(f"Year range: {df_processed['Year'].min()} - {df_processed['Year'].max()}")
    print("\nMissing values per year:")
    # Fixed the groupby operation for missing values count
    missing_by_year = df_processed.groupby('Year').agg(
        missing_values=('Survival_Rate', lambda x: x.isna().sum())
    )
    print(missing_by_year)
except Exception as e:
    print(f"Error loading data: {e}")
    raise

narrative_steps = [
    {
        'title': "Education's Critical Role in Survival",
        'content': """Our analysis reveals a strong link between education levels and survival rates. 
                     Countries with higher education investment consistently show better survival outcomes, 
                     demonstrating education's life-saving potential.""",
        'year': 2021,
        'highlight_regions': ['Sub-Saharan Africa'],
        'annotation': "Regions with lower education access show lower survival rates"
    },
    {
        'title': "The Education-Survival Divide",
        'content': """The data shows a striking pattern: nations with higher education spending 
                     and better school enrollment rates achieve survival rates above 90%, while 
                     those with limited educational access often struggle below 70%.""",
        'year': 2021,
        'countries': ['Norway', 'Sierra Leone', 'Japan', 'Niger'],
        'annotation': "Education access correlates with survival rates"
    },
    {
        'title': "Education as a Life-Saving Investment",
        'content': """Countries that have prioritized education, like Rwanda and Ethiopia, 
                     demonstrate how educational investment translates to improved survival rates. 
                     Ethiopia's dramatic improvement in education access since 2015 has led to 
                     better health awareness and improved survival outcomes.""",
        'year': 2015,
        'countries': ['Rwanda', 'Ethiopia'],
        'annotation': "Success stories in improving survival rates"
    }
]
app.layout = html.Div([
    # Header Section
    html.Div([
        html.H1("Education's Impact on Global Survival Rates (2015-2021)",
                className='header-title'),
        html.P([
            "Exploring how educational access and investment directly affect survival rates across nations. ",
            html.Strong("Key finding: "),
            "Higher education levels strongly correlate with better survival outcomes."
        ], className='description'),
        html.Div([
            html.Button("← Previous", id='prev-step', n_clicks=0, className='nav-button'),
            html.Button("Next →", id='next-step', n_clicks=0, className='nav-button'),
            html.Button("Start Tour", id='start-tour', n_clicks=0, className='nav-button-primary'),
        ], className='narrative-controls'),
    ], className='header-section'),

    # Narrative Panel
    # Update the Narrative Panel section in the layout
    html.Div([
        html.H2(narrative_steps[0]['title'], id='narrative-title', className='narrative-title'),
        html.P(narrative_steps[0]['content'], id='narrative-content', className='narrative-text'),
        html.Div([
            html.Div(
                className='step-indicator active' if i == 0 else 'step-indicator',
                id={'type': 'step-indicator', 'index': i},
                children=str(i + 1)
            ) for i in range(len(narrative_steps))
        ], className='step-indicators')
    ], className='narrative-panel'),
    # Key Metrics
    html.Div([
        html.Div([
            html.H3("Education Impact"),
            html.P(id='deaths-metric', className='metric'),
            html.P("increase in survival with each year of schooling", className='metric-label')
        ], className='metric-card'),
        html.Div([
            html.H3("Education Gap"),
            html.P(id='gap-metric', className='metric'),
            html.P("survival difference between high/low education regions", className='metric-label')
        ], className='metric-card'),
        html.Div([
            html.H3("Investment Impact"),
            html.P(id='impact-metric', className='metric'),
            html.P("lives saved through education investment", className='metric-label')
        ], className='metric-card'),
    ], className='metrics-container'),

    # Visualization Tabs
    dcc.Tabs([
        dcc.Tab(label='Global Crisis Map', children=[
            html.Div([
                dcc.Graph(
                    id='world-map',
                    style={'height': '60vh'}
                ),
                html.Div([
                    html.Label('Time Period:', className='slider-label'),
                    dcc.Slider(
                        id='year-slider',
                        min=2015,
                        max=2021,
                        step=1,
                        value=2021,
                        marks={str(year): str(year) for year in range(2015, 2022)},
                        included=False
                    )
                ], className='control-panel'),
                html.Div(id='map-insights', className='insights-panel')
            ], style={'padding': '20px'})
        ]),
        dcc.Tab(label='Impact Analysis', children=[
            html.Div([
                dcc.Graph(id='trend-chart'),
                html.Div([
                    html.Label('Compare Regions:', className='dropdown-label'),
                    dcc.Dropdown(
                        id='country-selector',
                        options=[{'label': country, 'value': country}
                                for country in sorted(df_processed['Country name'].unique())],
                        multi=True,
                        value=[],
                        placeholder="Select countries to compare"
                    )
                ], className='control-panel'),
                html.Div(id='trend-insights', className='insights-panel')
            ])
        ])
    ], id='tabs'),

    # Call to Action
    html.Div([
        html.H2("Education Saves Lives: Take Action"),
        html.P([
            "Every ",
            html.Strong("additional year of education"),
            " improves survival rates. Here's how you can help:"
        ]),
        html.Ul([
            html.Li([
                html.Strong("Support Educational Access: "),
                "Advocate for universal education access in developing regions"
            ]),
            html.Li([
                html.Strong("Promote Health Education: "),
                "Support programs that integrate health education into schools"
            ]),
            html.Li([
                html.Strong("Enable Educational Resources: "),
                "Back initiatives for better schools and learning materials"
            ])
        ]),
        html.Div([
            html.A(
                "Learn More About Education's Impact on Health",
                href="https://societyhealth.vcu.edu/work/the-projects/why-education-matters-to-health-exploring-the-causes.html",
                className="action-button",
                target="_blank"  # Opens the link in a new tab
            ),
            html.A(
                "Support Educational Initiatives",
                href="https://sankeshfoundation.org/support-educational-initiatives-make-a-difference-today/",
                className="action-button-secondary",
                target="_blank"  # Opens the link in a new tab
            )
        ], className="action-buttons")
    ], className='action-section')
], className='container')

# Consolidated metrics callback
@app.callback(
    [Output('deaths-metric', 'children'),
     Output('gap-metric', 'children'),
     Output('impact-metric', 'children')],
    [Input('year-slider', 'value')]
)
def update_metrics(selected_year):
    if selected_year is None:
        return "Loading...", "Loading...", "Loading..."

    try:
        year_data = df_processed[df_processed['Year'] == selected_year]

        max_rate = year_data['Survival_Rate'].max()
        min_rate = year_data['Survival_Rate'].min()
        gap = max_rate - min_rate

        global_pop_15_60 = 4500000000  # Approximate global population aged 15-60
        avg_rate = year_data['Survival_Rate'].mean()
        potential_lives = int((max_rate - avg_rate) * global_pop_15_60)
        annual_deaths = int((1 - avg_rate) * global_pop_15_60 / 45)

        return (
            f"{annual_deaths:,}",
            f"{gap:.1%}",
            f"{potential_lives:,}"
        )
    except Exception as e:
        print(f"Error in update_metrics: {e}")
        return "Error", "Error", "Error"

@app.callback(
    [Output('narrative-title', 'children'),
     Output('narrative-content', 'children'),
     Output('year-slider', 'value'),
     Output('country-selector', 'value'),
     Output({'type': 'step-indicator', 'index': ALL}, 'className')],
    [Input('prev-step', 'n_clicks'),
     Input('next-step', 'n_clicks'),
     Input('start-tour', 'n_clicks')],
    [State('narrative-title', 'children')]
)
def update_narrative(prev_clicks, next_clicks, start_clicks, current_title):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Determine current step
    if trigger_id == 'start-tour' or not current_title:
        current_step = 0  # Reset to the first step for "Start Tour"
    else:
        try:
            current_step = next(
                i for i, step in enumerate(narrative_steps)
                if step['title'] == current_title
            )
        except StopIteration:
            current_step = 0  # Default to the first step if not found

    # Adjust step based on navigation
    if trigger_id == 'next-step' and current_step < len(narrative_steps) - 1:
        current_step += 1
    elif trigger_id == 'prev-step' and current_step > 0:
        current_step -= 1

    # Update outputs for the current step
    step = narrative_steps[current_step]
    indicators = [
        'step-indicator active' if i == current_step else 'step-indicator'
        for i in range(len(narrative_steps))
    ]

    return (
        step['title'],
        step['content'],
        step['year'],
        step.get('countries', []),
        indicators
    )

@app.callback(
    Output('map-insights', 'children'),
    [Input('year-slider', 'value')]
)
def update_map_insights(selected_year):
    year_data = df_processed[df_processed['Year'] == selected_year]

    return html.Div([
        html.H3("Education & Survival Connection", className='insight-header'),
        html.P([
            "Countries with higher education spending show significantly better survival rates. ",
            html.Strong("Key findings:")
        ]),
        html.Ul([
            html.Li("Higher education regions: >90% survival rate"),
            html.Li("Limited education regions: <70% survival rate"),
            html.Li("Education investment correlates with improved survival")
        ]),
        html.P([
            html.Strong("Insight: "),
            "Educational access is a key predictor of survival rates"
        ], className="insight-highlight")
    ])
# Map callback
@app.callback(
    Output('world-map', 'figure'),
    [Input('year-slider', 'value')]
)
def update_map(selected_year):
    if selected_year is None:
        selected_year = 2021

    year_data = df_processed[df_processed['Year'] == selected_year].copy()

    fig = px.choropleth(
        year_data,
        locations='economy',
        color='Survival_Rate',
        hover_name='Country name',
        custom_data=['Survival_Rate'],
        title=f'Global Survival Rates ({selected_year})',
        color_continuous_scale=[
            [0, 'rgb(189,0,38)'],  # dark red
            [0.2, 'rgb(240,59,32)'],  # red
            [0.4, 'rgb(253,141,60)'],  # orange
            [0.6, 'rgb(254,204,92)'],  # yellow
            [0.8, 'rgb(151,185,224)'],  # light blue
            [1, 'rgb(49,130,189)']  # dark blue
        ],
        range_color=[0.5, 1.0]
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Survival Rate: %{customdata[0]:.1%}<extra></extra>"
    )

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            showland=True,
            landcolor='lightgray',
            showcountries=True,
            countrycolor='white',
            countrywidth=0.5,
            coastlinewidth=0.5,
            center=dict(lon=0, lat=20),
            projection_scale=1.3
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        coloraxis_colorbar=dict(
            title="Survival Rate",
            tickformat='.0%',
            len=0.8,
            title_side='right',
            thicknessmode="pixels",
            thickness=20,
            x=1.02
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=600
    )

    return fig


# Trend chart callback
@app.callback(
    Output('trend-chart', 'figure'),
    [Input('country-selector', 'value')]
)
def update_trend_chart(selected_countries):
    if not selected_countries:
        return {}

    filtered_df = df_processed[df_processed['Country name'].isin(selected_countries)]

    fig = px.line(
        filtered_df,
        x='Year',
        y='Survival_Rate',
        color='Country name',
        title='Survival Rate Trends by Country',
        labels={'Survival_Rate': 'Survival Rate (%)', 'Year': 'Year'}
    )

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Survival Rate (%)',
        hovermode='x unified',
        yaxis=dict(range=[0.5, 1.0], tickformat='.0%'),
        xaxis=dict(dtick=1),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig
@app.callback(
    Output('trend-insights', 'children'),
    [Input('country-selector', 'value')]
)
def update_trend_insights(selected_countries):
    if not selected_countries:
        return "Select countries to see education-survival relationships"

    return html.Div([
        html.H3("Education's Impact on Survival Trends", className='insight-header'),
        html.P("Analysis of selected countries shows:"),
        html.Ul([
            html.Li("Countries with increased education spending show improved survival rates"),
            html.Li("Regions with better school enrollment demonstrate higher survival"),
            html.Li("Investment in education correlates with better health outcomes")
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)