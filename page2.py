import dash
from dash import  dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd  

import numpy as np
import plotly.graph_objects as go
import pandas as pd
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout about content", className="lead"
        ),
        
    ],
    style=SIDEBAR_STYLE,
)

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
    so2_current = emis_df.iloc[6:11,[12,13,14,15]].reset_index(drop=True)

    so2_current.columns = ["Industry","2025","2030","2040"]
    so2_current["Scenario"] = "Current Policy"
    so2_current["Country"] = sheet
    so2_current["Emission"] = "SO2"

    # nox emissions for current policy
    nox_current = emis_df.iloc[13:18,[12,13,14,15]].reset_index(drop=True)

    nox_current.columns = ["Industry","2025","2030","2040"]
    nox_current["Scenario"] = "Current Policy"
    nox_current["Country"] = sheet
    nox_current["Emission"] = "NOx"

    # pm emissions for current policy
    pm_current = emis_df.iloc[20:25,[12,13,14,15]].reset_index(drop=True)

    pm_current.columns = ["Industry","2025","2030","2040"]
    pm_current["Scenario"] = "Current Policy"
    pm_current["Country"] = sheet
    pm_current["Emission"] = "PM"
    
    current_policy = pd.concat([so2_current,nox_current,pm_current],ignore_index=True)
    
    # so2 emissions for sustainable development policy
    so2_sus = emis_df.iloc[6:11,[12,20,21,22]].reset_index(drop=True)

    so2_sus.columns = ["Industry","2025","2030","2040"]
    so2_sus["Scenario"] = "Sustainable Development"
    so2_sus["Country"] = sheet
    so2_sus["Emission"] = "SO2"

    # nox emissions for sustainable development policy
    nox_sus = emis_df.iloc[13:18,[12,20,21,22]].reset_index(drop=True)

    nox_sus.columns = ["Industry","2025","2030","2040"]
    nox_sus["Scenario"] = "Sustainable Development"
    nox_sus["Country"] = sheet
    nox_sus["Emission"] = "NOx"

    # pm emissions for sustainable development policy
    pm_sus = emis_df.iloc[20:25,[12,20,21,22]].reset_index(drop=True)

    pm_sus.columns = ["Industry","2025","2030","2040"]
    pm_sus["Scenario"] = "Sustainable Development"
    pm_sus["Country"] = sheet
    pm_sus["Emission"] = "PM"
    
    sus_policy = pd.concat([so2_sus,nox_sus,pm_sus],ignore_index=True)
    df = pd.concat([stated_policy,current_policy,sus_policy],ignore_index=True)
    df1 = pd.concat([df1,df],ignore_index=True)

df1 = df1.fillna(0)

countries = df1.Country.unique() 

# Line Chart
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
# Landing Page
# color_discrete_map={'(?)':'black', 'Lunch':'gold', 'Dinner':'darkblue'}
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

content  = html.Div(
    style={'background-image':'url("/assets/Save_Water_Poster_Background.jpg")','height':'100vh','backgroundColor': colors['background']},children=[
    html.Div(children=[
        html.H1(children='Enabling Responsible production and Green consumption', style={'textAlign': 'center','color': colors['text'],"margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
        ### Sunburst chart 
        

        html.Div(children='''
        Emissions of sunburst
        ''',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
        dcc.Dropdown(id = 'country',
        options = [{'label':x ,'value':x} for x in sorted (food_sunburst.Country.unique())],
        placeholder="Select a country",
        value = 'US',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width':'50%',
        'verticalAlign':"middle",
        "margin-left": "24rem",
        "margin-right": "2rem",
        "padding": "10px 10px"}),

        dcc.Graph(
            id='graph1',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}
            
        ),    
        dcc.Graph(
            id='sankey-chart',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}
            
        )
    
        

            ])
])
@app.callback(
    Output(component_id = 'graph1' ,component_property = 'figure' ),
    [Input(component_id = 'country',component_property = 'value')])

def update_sunburst(country):
    fig1 = px.sunburst(food_sunburst[food_sunburst["Country"]==country],
            path=['Country', 'GHG','Food System Stage'],
            values='GHG Emissions',
            hover_data=["GHG"],
            title = "Current emissions of air pollutants")
    fig1.update_layout(paper_bgcolor=colors['background'])
    return fig1

@app.callback(
    Output("sankey-chart", "figure"), 
    [Input("country", "value")])

def update_line_chart(country):
    mask = edgar_sankey['Country'].isin([country])
    
    fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 20,
      thickness = 20,
      line = dict(color = "grey", width = 0.5),
      label = [
          "Carbon dioxide (CO2)", "Methane (CH4)", "Nitrous oxide (N2O)",
          "F-gases", "Land", "Farm", "Processing",
          "Transport", "Packaging", "Retail", "Consumer", "Waste"],
      color = ["#3d6493", "#95ceeb", "#308bbc", "#86aad1", "#58805b", 
               "#98c7a0", "#f36e3a", "#fba644", "#ad5849", "#d2c795", "#736a62", "#b0a08c"]),
      link = dict(
          source = [emission_gas[i] for i in list(edgar_sankey[mask].GHG.values)], # corresponds to 4 GHGs (the 'sources')
          target = [stage[i] for i in list(edgar_sankey[mask]["Food System Stage"].values)], # corresponds to 8 food system stages (the 'targets') 
          value  = list(edgar_sankey[mask]["GHG Emissions"].values) #the amount per Source to Target
      ))])

    fig.update_layout(
        height=580,
        title_text="GHGs to Stages: Food System Emissions, 1990-2015", 
        font_size=14)
    return fig


app.layout = html.Div([ sidebar, content])

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0', port=8050)
