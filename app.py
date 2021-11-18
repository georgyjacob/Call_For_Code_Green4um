import dash
from dash import  dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.figure_factory as ff

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#C6C4C4"
}


# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


# path = "C:/Users/KD169FE/OneDrive - EY/Desktop/Call for  code/Application/"
raw_data = pd.ExcelFile("Call_for_code_Data.xlsx")
emis = pd.ExcelFile("emissions.xlsx")

app = dash.Dash(__name__) 

colors = {
    'background': '#fffcfc',
    'text': '#0c291f',
    'text1':'#000000'
}

## create data 
df1 = pd.DataFrame()
for sheet in emis.sheet_names[2:]:
    emis_df = emis.parse(sheet_name = sheet)
    # so2 emissions for stated policy
    so2 = emis_df.iloc[6:11,:6].reset_index(drop=True)

    so2.columns = ["Industry","2018","2025","2030","2035","2040"]
    so2["Scenario"] = "Stated Policy"
    so2["Country"] = sheet
    so2["Emission"] = "SO2"

    # nox emissions for stated policy
    nox = emis_df.iloc[13:18,:6].reset_index(drop=True)

    nox.columns = ["Industry","2018","2025","2030","2035","2040"]
    nox["Scenario"] = "Stated Policy"
    nox["Country"] = sheet
    nox["Emission"] = "NOx"

    # pm emissions for stated policy
    pm = emis_df.iloc[20:25,:6].reset_index(drop=True)

    pm.columns = ["Industry","2018","2025","2030","2035","2040"]
    pm["Scenario"] = "Stated Policy"
    pm["Country"] = sheet
    pm["Emission"] = "PM"
    
    stated_policy = pd.concat([so2,nox,pm],ignore_index=True)
    
    # so2 emissions for current policy
    so2_current = emis_df.iloc[6:11,[12,1,13,14,15]].reset_index(drop=True)

    so2_current.columns = ["Industry","2018","2025","2030","2040"]
    so2_current["Scenario"] = "Current Policy"
    so2_current["Country"] = sheet
    so2_current["Emission"] = "SO2"

    # nox emissions for current policy
    nox_current = emis_df.iloc[13:18,[12,1,13,14,15]].reset_index(drop=True)

    nox_current.columns = ["Industry","2018","2025","2030","2040"]
    nox_current["Scenario"] = "Current Policy"
    nox_current["Country"] = sheet
    nox_current["Emission"] = "NOx"

    # pm emissions for current policy
    pm_current = emis_df.iloc[20:25,[12,1,13,14,15]].reset_index(drop=True)

    pm_current.columns = ["Industry","2018","2025","2030","2040"]
    pm_current["Scenario"] = "Current Policy"
    pm_current["Country"] = sheet
    pm_current["Emission"] = "PM"
    
    current_policy = pd.concat([so2_current,nox_current,pm_current],ignore_index=True)
    
    # so2 emissions for sustainable development policy
    so2_sus = emis_df.iloc[6:11,[12,1,20,21,22]].reset_index(drop=True)

    so2_sus.columns = ["Industry","2018","2025","2030","2040"]
    so2_sus["Scenario"] = "Sustainable Development"
    so2_sus["Country"] = sheet
    so2_sus["Emission"] = "SO2"

    # nox emissions for sustainable development policy
    nox_sus = emis_df.iloc[13:18,[12,1,20,21,22]].reset_index(drop=True)

    nox_sus.columns = ["Industry","2018","2025","2030","2040"]
    nox_sus["Scenario"] = "Sustainable Development"
    nox_sus["Country"] = sheet
    nox_sus["Emission"] = "NOx"

    # pm emissions for sustainable development policy
    pm_sus = emis_df.iloc[20:25,[12,1,20,21,22]].reset_index(drop=True)

    pm_sus.columns = ["Industry","2018","2025","2030","2040"]
    pm_sus["Scenario"] = "Sustainable Development"
    pm_sus["Country"] = sheet
    pm_sus["Emission"] = "PM"
    
    sus_policy = pd.concat([so2_sus,nox_sus,pm_sus],ignore_index=True)
    df = pd.concat([stated_policy,current_policy,sus_policy],ignore_index=True)
    df1 = pd.concat([df1,df],ignore_index=True)

df1 = df1.fillna(0)

#heat map


energy_emissions = df1.fillna(0)

current_emissions = energy_emissions.loc[energy_emissions['Scenario']=='Current Policy'].groupby(['Country'], as_index = False).agg({'2018':'sum'})

country_dict = {'CHINA':'China',
                'INDIA':'India',
                'JPN':'Japan',
                'US':'United States of America',
                'RUS':'Russian Federation',
                'BRAZIL':'Brazil'}

current_emissions['country'] = current_emissions['Country'].map(country_dict)
current_emissions = current_emissions.dropna()

current_emissions['energy_emission_ratings'] = np.where(current_emissions['2018']>10,'High',
                                               np.where(current_emissions['2018']>3,'Medium','Low'))


countries = df1.Country.unique() 
line_chart = pd.melt(df1,
                    id_vars=["Industry","Scenario","Country","Emission"],
                    var_name="Year",
                    value_name="Emissions")
agg_view = line_chart.groupby(["Scenario","Country","Emission","Year"])["Emissions"].sum().reset_index()

food_df = raw_data.parse(sheet_name="Food")
emissions_2015 = food_df[food_df["Year"]==food_df["Year"].max()]["GHG Emissions"].sum()
food_sunburst = round((food_df[food_df["Year"]==food_df["Year"].max()].
groupby(["Country","Food System Stage","GHG"])["GHG Emissions"].sum().
sort_values(ascending=False)/emissions_2015)*100,2). reset_index()

edgar_sankey = food_df[(food_df["Year"]==2015)].groupby(by= ["GHG", 
                                    "FS Stage Order",
                                    "Food System Stage","Country"]).sum()[["GHG Emissions"]]
edgar_sankey = edgar_sankey.reset_index()

edgar_sankey["Stage"] = np.where(edgar_sankey["Food System Stage"].isin(["Land","Farm","Processing","Transport"])==True,"Production",
                        np.where(edgar_sankey["Food System Stage"].isin(["Packaging","Retail","Consumer"])==True,"Consumption",
                                edgar_sankey["Food System Stage"]))
all_countries = edgar_sankey.Country.unique()

heat_map = food_df[(food_df["Year"]==food_df["Year"].max())&\
                  (food_df['GHG Emissions']!=0)].reset_index(drop=True)
# Calculate rank for each country for the FS Stage
heat_map['stage_wise_rank'] = heat_map.groupby(["Food System Stage",'GHG'])["GHG Emissions"].rank("dense", ascending=False)
heat_map['stage_wise_rank'] = heat_map['stage_wise_rank'].astype(int)
# Pivot to get the wide view where columns denote each stage and contain ranks by stage emission - higher the worse
heat_map_pivot = pd.pivot_table(heat_map, values='stage_wise_rank', index='Country', columns='Food System Stage')
# # Remove any na records
heat_map_pivot = heat_map_pivot.dropna()
heat_map_pivot['country'] = heat_map_pivot.index

# Food emission ranking 
energy_emissions = df1.fillna(0)

current_emissions = energy_emissions.loc[energy_emissions['Scenario']=='Current Policy'].groupby(['Country'], as_index = False).agg({'2018':'sum'})

country_dict = {'CHINA':'China',
                'INDIA':'India',
                'JPN':'Japan',
                'US':'United States of America',
                'RUS':'Russian Federation',
                'BRAZIL':'Brazil'}

current_emissions['country'] = current_emissions['Country'].map(country_dict)
current_emissions = current_emissions.dropna()

current_emissions['energy_emission_ratings'] = np.where(current_emissions['2018']>10,'High',
                                               np.where(current_emissions['2018']>3,'Medium','Low'))

food_emissions_rankings = pd.merge(current_emissions[['country','energy_emission_ratings']],heat_map_pivot,on='country')

food_emissions_rankings.index = food_emissions_rankings['country'] + ', Energy Emission Level: ' + food_emissions_rankings['energy_emission_ratings']

fig = ff.create_annotated_heatmap(z = np.around(food_emissions_rankings.drop(['country','energy_emission_ratings'], axis=1).to_numpy(),0),
                                  y = food_emissions_rankings.drop(['country','energy_emission_ratings'], axis=1).index.tolist(),
                                  x = food_emissions_rankings.drop(['country','energy_emission_ratings'], axis=1).columns.tolist(),
                                  showscale=True,
                                  colorscale='RdYlGn',
                                font_colors=["black"],
                                hoverongaps=True)

emission_gas = {'Carbon dioxide (CO2)': 0,
                'Methane (CH4)': 1,
                'Nitrous oxide (N2O)': 2,
                'F-gases (Fluorinated)': 3}

stage = {'Land': 4,
         'Farm': 5,
         'Processing': 6,
         'Transport': 7,
         'Packaging': 8,
         'Retail': 9,
         'Consumer': 10,
         'Waste': 11}

st = {'Production':4,
     'Consumption':5,
     'Waste':6}



# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


index_page = html.Div(style={'background-image':'url("/assets/Background2.jpg")','height':'100vh',
  'width':'100%',
  'height':'100%',
  'top':'0px',
  'left':'0px',
  'backgroundColor': colors['background']},
children=[
    html.Div(children=[
        html.H1(children='Enabling responsible production lines and green consumption links', style={'textAlign': 'center','color': colors['text'],"margin-left": "2rem",
        "margin-right": "2rem"
        }),
    
     html.Div(children='''
        Energy is the backbone of modern economy. Emissions from energy sector have been high globally due to the high dependence on energy for any of the economic activity in the industrial world. This website intends to illustrate how sustainable development efforts will make impact in future through its domino effect across sectors.
For illustration purposes, we use the food processing sector and bring out a view to help policymakers across countries design tax reforms to support sustainable developmental efforts. These choices that will shape our energy use, our environment and our wellbeing through directed focus in each sector
        ''',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
        dcc.Dropdown(id = 'country',
        options = [{'label':x ,'value':x} for x in sorted (df1.Country.unique())],
        placeholder="Select a country",
        value = 'US',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width':'50%',
        'verticalAlign':"middle",
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "10px 10px"}),

        dcc.Graph(
            id='graph1',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "24rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}
            
        )       
    ,
        ### Line  chart
       html.Div(children='''
        These charts represent how energy emissions projections for future time periods will vary depending on policies adopted today.
        ''',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
        dcc.Dropdown(id = 'emission',
        options = [{'label':x ,'value':x} for x in sorted (df1.Emission.unique())],
        placeholder="Select a emission",
        value = 'PM',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width':'50%',
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "10px 10px"}),

        dcc.Graph(
            id='graph3',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "24rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}
            
        ) ,
        dcc.Link('Go to Page 1', href='/page-1'),
    html.Br(),
    ])
])
@app.callback(
    Output(component_id = 'graph1' ,component_property = 'figure' ),
    [Input(component_id = 'country',component_property = 'value')])

def update_sunburst(country):
    fig1 = px.sunburst(df1[df1["Country"] ==country], 
                  path=['Country', 'Emission','Industry'], 
                  values='2018',
                  hover_data=["Emission"],
                  title = "Current emissions of air pollutants")
    fig1.update_layout(paper_bgcolor=colors['background'])
    return fig1


@app.callback(
    Output(component_id = 'graph3' ,component_property = 'figure' ),
    [Input(component_id = 'country',component_property = 'value'),
    Input(component_id = 'emission',component_property = 'value')]
)

def update_line(country,emission):
    fig3 = px.line(line_chart[(line_chart.Year.isin(['2018','2025','2030','2040']))&
                          (line_chart["Country"]== country )&
                          (line_chart["Emission"]== emission)].
              groupby(["Year","Country","Emission","Scenario"]).
              agg({'Emissions':sum}).
              reset_index(), 
              
              x="Year", 
              y="Emissions", 
              color='Scenario')
    fig3.update_layout(paper_bgcolor=colors['background'])
    return fig3
    

page_1_layout = html.Div(
    style={'background-image':'url("/assets/Background2.jpg")','height':'100vh','backgroundColor': colors['background'],
  'width':'100%',
  'height':'100%',
  'top':'0px',
  'left':'0px'},children=[
    html.Div(children=[
        html.H1(children='Food processing sector', style={'textAlign': 'center','color': colors['text'],"margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
        ### Sunburst chart 
        

        html.Div(children='''
        Food processing has close backward and forward linkages. Due to the perishable nature of products, this industry has substantially organic waste that can be naturally recycled but due to the direct involvement in food chain, any contamination here is dangerous to human race itself. Our analysis aims at understanding how different stages of food processing industry causes environmental pollution through emission of CO2, CH4, N2O and other gases
        ''',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
        dcc.Dropdown(id = 'country1',
        options = [{'label':x ,'value':x} for x in sorted (food_sunburst.Country.unique())],
        placeholder="Select a country",
        value = 'India',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width':'50%',
        'verticalAlign':"middle",
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "10px 10px"}),

        dcc.Graph(
            id='graph_sun',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "24rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}
            
        ),    
        html.Div(children='''
        We have categorized the different stages of food processing industry in to production, consumption and waste creation activity zones. This zoning helps us understand how policy actions should be directed at a macro level and hence promote positive externality or reduce negative externality from these activities
        ''',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),

        dcc.Graph(
            id='sankey-chart',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "24rem",
        "margin-right": "2rem",
        }
            

    ),
    html.Div(children='''
        Since, energy sector is the backbone of economic activity within a nation, we benchmarked our sector analysis on the same. If a country is placed on lower side of the spectrum in energy emissions and has a high emission stage for particular sector, food processing in current page, we will flag this as a risk to manage through corrective policy action. Similarly, if there is a country that is placed on higher side of the spectrum in energy emissions and has a low emission stage for particular sector, food processing in current page, we will flag this as an opprotunity to incentivize and learn from this stage. Potentially, a deep dive to the stage in history can give us answers to problems faced by other stages/activities/sectors/economies ''',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
    dcc.Graph(figure=fig),
    html.Div(id='page-1-content'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
    
    ])
])
@app.callback(
    Output(component_id = 'graph_sun' ,component_property = 'figure' ),
    [Input(component_id = 'country1',component_property = 'value')])

def update_sunburst(country1):
    fig1 = px.sunburst(food_sunburst[food_sunburst["Country"]==country1],
            path=['Country', 'GHG','Food System Stage'],
            values='GHG Emissions',
            hover_data=["GHG"],
            title = "Current emissions of air pollutants")
    fig1.update_layout(paper_bgcolor=colors['background'])
    return fig1

@app.callback(
    Output("sankey-chart", "figure"), 
    [Input("country1", "value")])

def update_line_chart(country1):
    mask = edgar_sankey['Country'].isin([country1])
    
    fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 20,
      thickness = 20,
      line = dict(color = "grey", width = 0.5),
      label = [
          "Carbon dioxide (CO2)", "Methane (CH4)", "Nitrous oxide (N2O)",
          "F-gases", "Production","Consumption","Waste"],
      color = ["#3d6493", "#95ceeb", "#308bbc", "#86aad1", "#58805b", 
               "#98c7a0", "#f36e3a", "#fba644", "#ad5849", "#d2c795", "#736a62", "#b0a08c"]),
      link = dict(
          source = [emission_gas[i] for i in list(edgar_sankey[mask].GHG.values)], # corresponds to 4 GHGs (the 'sources')
          target = [st[i] for i in list(edgar_sankey[mask]["Stage"].values)], # corresponds to 8 food system stages (the 'targets') 
          value  = list(edgar_sankey[mask]["GHG Emissions"].values) #the amount per Source to Target
      ))])

    fig.update_layout(
        height=580,
        title_text="GHGs to Stages: Food System Emissions, 1990-2015", 
        font_size=14)
    return fig

    


@app.callback(dash.dependencies.Output('page-1-content', 'children'),
              [dash.dependencies.Input('page-1-dropdown', 'value')])
def page_1_dropdown(value):
    return 'You have selected "{}"'.format(value)



# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0', port=8050)
