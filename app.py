# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 11:12:11 2020

@author: user
"""


import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import numpy as np
import io
import simplejson
import requests
import folium
from folium.plugins import MarkerCluster
#import json
import dash_table
import plotly.graph_objects as go

data_path = 'https://raw.githubusercontent.com/pratik-bose/CoronaTracker/V1/'

#Load India data
#Import Lat Long
s = requests.get(str(data_path)+ 'GeoData.csv').content
LLi = pd.read_csv(io.StringIO(s.decode('utf-8')))
#Import GeoJson file
IJ = requests.get(str(data_path)+ 'indian_states2.json').content
JSi = simplejson.loads(IJ)

#Load World data
#Import Lat Long
s = requests.get(str(data_path)+ 'CountryLL.csv').content
LLw = pd.read_csv(io.StringIO(s.decode('utf-8')))
#Import GeoJson file
IJ = requests.get(str(data_path)+ 'world-countries.json').content
JSw = simplejson.loads(IJ)

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '12px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '12px'
}

########### Map Plot ################
def CreateMapPlot(data, ll, js, var,id):
    if id == 1:
        key = "feature.properties.st_nm"
        lcn = [20.5937,78.9629]
        zm = 4
    elif id == 2:
        key = "feature.properties.name"
        lcn = [20, 0]
        zm = 1
        
    df = data[data.Date == max(data.Date)]    
    df = pd.merge(df, ll, on='Name_1', how='left')
    
    for i in range(0,len(df)):
        df.loc[i,'StateInfo'] = df.loc[i,'Name_1'] \
            + ', '+var+' :' + str('{:,.0f}'.format(df.loc[i,var]))

    df1 = df[df[var]>0]
    # Initialize the map:
    m = folium.Map(location=lcn, tiles="OpenStreetMap", zoom_start=zm,height ='100%',width = '100%',bottom = '0%',trackResize=True)

    m.choropleth(
     geo_data=js,
     name='choropleth',
     data=df1,
     columns=['Name_2',var],
     key_on= key,
     fill_color='OrRd',
     fill_opacity=0.7,
     line_opacity=0.2,
     legend_name=var,
     highlight = True
    )
    marker_cluster = MarkerCluster().add_to(m)
    
    df1 = df1[df1['Latitude'].notna()]
    for i in range(0,len(df1)):
        folium.Marker(
                  location=[df1.iloc[i]['Latitude'], df1.iloc[i]['Longitude']],
                  popup=df1.iloc[i]['StateInfo']
               ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)
    print("Plot Created")
    return(m._repr_html_())


######### Line Plot #########
def generateplot(value,col,fdf,id):
    if id == 1:
        nm = 'India'
    elif id == 2:
        nm = 'World'
        
    if col == 'TotalCases':
        #title = "Confirmed Cases"
        clr = 'blue'
    elif col == 'NewCases':
        #title = "New Cases"
        clr = 'orange'
    elif col == 'ActiveCases':
        #title = 'Active Cases'
        clr = 'purple'
    elif col == "Recovered":
        #title = "Total Recovered"
        clr = 'green'
    elif col == "Death":
        #title = "Total Deaths"
        clr = 'red'
        
    x = fdf[col]
    #fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    annotations=[] 
    for i in [nm,value]:
        fig.add_trace(go.Scatter(x=x.index,y= x[i], name=i,opacity= 1 if i == value else 1 if i == nm else 0.3,
                                 line = dict(color= clr if i == value else "black" if i == nm else 'grey'))
                      ,secondary_y=True if i == value else False
                      )
        annotations.append(dict(xref='paper', x=0.8 if i == value else 0.2, y= max(x[nm])+100,
                         xanchor='right' if i == value else 'left', yanchor='middle',
                         text= i + ' -->' if i == value else '<-- ' +i,
                         opacity= 1 if i == value else 1 if i == nm else 0.3,
                         font=dict(color = clr if i == value else "black" if i == nm else 'grey'),
                         showarrow=False))
        
    
    # Set y-axes titles
    #fig.update_yaxes(title_text=nm, secondary_y=False)
    #fig.update_yaxes(title_text= 'State' if id == 1 else 'Country', secondary_y=True)    
    fig.update_layout(annotations=annotations,showlegend=False
                      ,margin=dict(t=10,b=10,l=10,r=10,pad=2),height=150
                      #,legend_orientation="h",legend=dict(x=.4, y=-0.35)
                      )
    return(fig)



######### Create Layout ###########        
def create_layout(data_path):
#from WebScrapper3 import DtaScrapper
    global Wdt, mdt
    
    # Load base data India
    s = requests.get(str(data_path)+ 'CoronaData.csv').content
    mdt = pd.read_csv(io.StringIO(s.decode('utf-8')))
    # Load base data World
    s = requests.get(str(data_path)+ 'WorldCoronaData.csv').content
    Wdt = pd.read_csv(io.StringIO(s.decode('utf-8')))
    print('Data load complete..')
    
    mdf = mdt[mdt.Date==max(mdt.Date)]
    mdf = mdf.sort_values(by=['TotalCases', 'NewCases',"ActiveCases", "Recovered", "Death"], ascending=False)
    mdf = mdf.assign(slno = range(1,len(mdf)+1))
    mdf = mdf[['slno','Name_1', 'TotalCases', 'NewCases',"ActiveCases", "Recovered", "Death","NoNewCasesSince"]]
    mdf.columns = ['Sl.No','Name', 'Confirmed', 'New',"Active", "Recovered", "Deaths",'No Cases Since']
    mdf['Confirmed'] = mdf.apply(lambda x: "{:,}".format(x['Confirmed']), axis=1)
    mdf['New'] = mdf.apply(lambda x: "{:,}".format(x['New']), axis=1)
    mdf['Active'] = mdf.apply(lambda x: "{:,}".format(x['Active']), axis=1)
    mdf['Recovered'] = mdf.apply(lambda x: "{:,}".format(x['Recovered']), axis=1)
    mdf['Deaths'] = mdf.apply(lambda x: "{:,}".format(x['Deaths']), axis=1)
    
    wdf = Wdt[Wdt.Date==max(Wdt.Date)]
    wdf = wdf.sort_values(by=['TotalCases', 'NewCases',"ActiveCases", "Recovered", "Death"], ascending=False)
    wdf = wdf.assign(slno = range(1,len(wdf)+1))
    wdf = wdf[['slno','Name_1', 'TotalCases', 'NewCases',"ActiveCases", "Recovered", "Death","NoNewCasesSince"]]
    wdf.columns = ['Sl.No','Name', 'Confirmed', 'New',"Active", "Recovered", "Deaths","No Cases Since"]
    wdf['Confirmed'] = wdf.apply(lambda x: "{:,}".format(x['Confirmed']), axis=1)
    wdf['New'] = wdf.apply(lambda x: "{:,}".format(x['New']), axis=1)
    wdf['Active'] = wdf.apply(lambda x: "{:,}".format(x['Active']), axis=1)
    wdf['Recovered'] = wdf.apply(lambda x: "{:,}".format(x['Recovered']), axis=1)
    wdf['Deaths'] = wdf.apply(lambda x: "{:,}".format(x['Deaths']), axis=1)    
    
    TC1 = sum(mdt.loc[mdt.Date==max(mdt.Date),'TotalCases'])
    TC = '{:,.0f}'.format(TC1)
    NC = '{:,.0f}'.format(sum(mdt.loc[mdt.Date==max(mdt.Date),'NewCases']))
    AC = sum(mdt.loc[mdt.Date==max(mdt.Date),'ActiveCases'])
    AC = '{:,.0f}'.format(AC)+" ("+str(round((AC/TC1)*100,2))+"%)"
    RE = sum(mdt.loc[mdt.Date==max(mdt.Date),'Recovered'])
    RE = '{:,.0f}'.format(RE)+" ("+str(round((RE/TC1)*100,2))+"%)"
    DT = sum(mdt.loc[mdt.Date==max(mdt.Date),'Death'])
    DT = '{:,.0f}'.format(DT)+" ("+str(round((DT/TC1)*100,2))+"%)"
    TM = max(mdt.loc[mdt.Date==max(mdt.Date),'Time'])
    DT_TM = str(max(mdt.Date)+' '+TM)
    
    WTC1 = sum(Wdt.loc[Wdt.Date==max(Wdt.Date),'TotalCases'])
    WTC = '{:,.0f}'.format(WTC1)
    WNC = '{:,.0f}'.format(sum(Wdt.loc[Wdt.Date==max(Wdt.Date),'NewCases']))
    WAC = sum(Wdt.loc[Wdt.Date==max(Wdt.Date),'ActiveCases'])
    WAC = '{:,.0f}'.format(WAC)+" ("+str(round((WAC/WTC1)*100,2))+"%)"
    WRE = sum(Wdt.loc[Wdt.Date==max(Wdt.Date),'Recovered'])
    WRE = '{:,.0f}'.format(WRE)+" ("+str(round((WRE/WTC1)*100,2))+"%)"
    WDT = sum(Wdt.loc[Wdt.Date==max(Wdt.Date),'Death'])
    WDT = '{:,.0f}'.format(WDT)+" ("+str(round((WDT/WTC1)*100,2))+"%)"
    WTM = max(Wdt.loc[Wdt.Date==max(Wdt.Date),'Time'])
    WDT_TM = str(max(Wdt.Date)+' '+WTM)


#### Define Layout ####
    return html.Div([
        #Navigation Bar
        dbc.NavbarSimple(#style={'font-size': "150%"}#,'height': '15px'}#, 'width': '100px', 'min-height': '1px' }
            children=[
                dbc.DropdownMenu(
                        children=[
                                dbc.DropdownMenuItem("Data Sources", header=True),
                                dbc.DropdownMenuItem(divider=True),
                                dbc.DropdownMenuItem("1) Ministry of Health and Family Welfare, India", href="https://www.mohfw.gov.in/"),
                                html.P("Total affected States & UTs : " + str(len(mdt.Name_1.unique())) +
                                ". Data last fetched on : " + DT_TM + " IST",className="text-muted px-4 mt-4"),
                                dbc.DropdownMenuItem("2) Worldometer", href="https://www.worldometers.info/"),
                                html.P("Total affected Countries & Territories : " + str(len(Wdt.Name_1.unique())) +
                                ". Data last fetched on : " + WDT_TM + " EST",className="text-muted px-4 mt-4"),
                                dbc.DropdownMenuItem(divider=True),
                                dbc.Card(body = True, children = [
                                    dcc.Markdown([
                                         '''
                                         ##### Info:
                                         Historical data has been extracted from multiple sources and at different time of the day. \
                                         Also, data for Indian-states and Countries are taken from two different sources.
                                         
                                         As a result - data may or maynot match.
                                         '''
                                         ])
                                ]),
                                dbc.DropdownMenuItem(divider=True),
                                html.P(
                                    "Mail at pratik.bose@outlook.com for any feedback."
                                    ,className="text-muted px-4 mt-4",
                                ),
                                html.P(
                                    "Created by Pratik Bose"
                                    ,className="text-muted px-4 mt-4",
                                ),
                                dbc.DropdownMenuItem(divider=True),
                                html.P(
                                    "V2.4.19"
                                    ,className="text-muted px-4 mt-4",
                                )
                           ],
                            nav=True,
                            in_navbar=True,
                            label="More",
                            #style={'font-size': "150%",'align':'left'}#,'height': '15px'}#, 'width': '100px', 'min-height': '1px' }
                            right=True
                            ),
                    ],
                    brand= "Coronavirus COVID-19 Cases",
                    color="secondary",
                    dark=True,
                    fluid = True
            )#Navigation Bar
            #Main Body
        ,html.Div([
            #Main Tab Item
            dbc.Tabs(style ={'fontWeight': 'bold','font-size': "150%"},children=[
                # India Tab
                dbc.Tab(label = "India",  tabClassName="ml-auto",children=[
                ###############################
                    #Total Level cards
                        dbc.CardGroup([
                            dbc.Card([
                                    html.P("Confirmed Cases",className="card-text")
                                    ,html.P(TC, className="card-title")
                                    ]
                                    , color="primary", body = True),
                            dbc.Card([
                                    html.P("New Cases",className="card-text")
                                    ,html.P(NC, className="card-title")
                                    ]
                                    , color="warning", body=True),
                            dbc.Card([
                                    html.P("Active Cases",className="card-text")
                                    ,html.P(AC, className="card-title")
                                    ]
                                    , color="info", body=True),
                            dbc.Card([
                                    html.P("Recovered",className="card-text")
                                    ,html.P(RE, className="card-title")
                                    ]
                                    , color="success", body=True),
                            dbc.Card([
                                    html.P("Deaths",className="card-text")
                                    ,html.P(DT, className="card-title")
                                    ]
                                    , color="danger", body=True)
                            ]
                            ,style={'textAlign': 'center','fontWeight': 'bold','font-size': "160%", 'color':'white'}
                            )#Total Level cards
                        # Map body
                        ,dbc.Card(body = True, children = [
                            dbc.Row([
                                dbc.Col(width = 1),
                                dbc.Col(width = 10,children =[
                                    dbc.Tabs(id = "mMainTab",children=[
                                        dbc.Tab(label = "Confirmed Case",tabClassName="ml-auto",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(mdt, LLi, JSi, 'TotalCases',1), width = '100%', height = '370')]
                                                ),
                                        dbc.Tab(label = "New Case",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(mdt, LLi, JSi, 'NewCases',1), width = '100%', height = '370')]
                                                ),
                                        dbc.Tab(label = "Active Case",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(mdt, LLi, JSi, 'ActiveCases',1), width = '100%', height = '370')]
                                                ),
                                        dbc.Tab(label = "Recovered",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(mdt, LLi, JSi, 'Recovered',1), width = '100%', height = '370')]
                                                ),        
                                        dbc.Tab(label = "Death",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(mdt, LLi, JSi, 'Death',1), width = '100%', height = '370')]
                                                ),
                                        dbc.Tab(label = "Data",tabClassName="mr-auto",children = [
                                            dbc.Card(body = True, style={'height':'100%', 'width':'370'}, children=[
                                                dash_table.DataTable(
                                                        #id='table',
                                                        columns=[{"name": i, "id": i} for i in mdf.columns],
                                                        data=mdf.to_dict('records'),
                                                        style_cell={'textAlign': 'Center','width': '80px','fontSize':12},
                                                        style_table={'maxHeight': '370px','overflowY':'scroll'},
                                                        fixed_rows={ 'headers': True, 'data': 0 },
                                         #               style_as_list_view=True,
                                                        style_cell_conditional=[
                                                            {'if': {'column_id': "Sl.No"},
                                                                'backgroundColor': '#6c757d',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            } ,
                                                            {'if': {'column_id': 'Name'},
                                                                'backgroundColor': '#6c757d',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            } ,
                                                            {'if': {'column_id': 'No Cases Since'},
                                                                'backgroundColor': '#6c757d',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            } ,
                                                            {'if': {'column_id': 'Confirmed'},
                                                                'backgroundColor': '#01A9DB',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            },
                                                            {'if': {'column_id': 'New'},
                                                                'backgroundColor': '#FF8000',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            },
                                                            {'if': {'column_id': 'Active'},
                                                                'backgroundColor': '#9F81F7',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            },
                                                            {'if': {'column_id': 'Recovered'},
                                                                'backgroundColor': '#28a745',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            },
                                                            {'if': {'column_id': 'Deaths'},
                                                                'backgroundColor': '#dc3545',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            }
                                                            
                                                          ]
                                                        )
                                                ])
                                            ])
                                        ])
                                    ]),
                                dbc.Col(width = 1),
                                ])
                            ])# Map body
                        ,html.Br()
                        #granular drop down
                        ,dbc.Row([
                            dbc.Col(["Select State - "], width = 4,style = {'textAlign':'right','fontWeight': 'bold'}),
                            dbc.Col(width = 4, children=[
                                dcc.Dropdown(
                                        id='dd',
                                        options=[{'label':cl, 'value':cl} for cl in list(sorted(mdf.Name.unique()))],
                                        value = 'West Bengal',
                                        clearable=False,
                                        placeholder="Select a state"
                                        #,style={'font-size': "110%"}#'height': '2px', 'width': '100px', 'font-size': "50%",'min-height': '1px' }
                                    )
                                ]),
                            dbc.Col(width = 4)
                            ])#granular drop down
                        ,html.Br()
                        #Granular Level cards
                        ,dbc.CardGroup([
                            dbc.Card([
                                    html.P("Confirmed Cases",className="card-text")
                                    ,html.P(id = 'mTC', className="card-title")
                                    ]
                                    , color="primary", body = True),
                            dbc.Card([
                                    html.P("New Cases",className="card-text")
                                    ,html.P(id = 'mNC', className="card-title")
                                    ]
                                    , color="warning", body=True),
                            dbc.Card([
                                    html.P("Active Cases",className="card-text")
                                    ,html.P(id = 'mAC', className="card-title")
                                    ]
                                    , color="info", body=True),
                            dbc.Card([
                                    html.P("Recovered",className="card-text")
                                    ,html.P(id = 'mRC', className="card-title")
                                    ]
                                    , color="success", body=True),
                            dbc.Card([
                                    html.P("Deaths",className="card-text")
                                    ,html.P(id = 'mDC', className="card-title")
                                    ]
                                    , color="danger", body=True)
                            ]
                            ,style={'textAlign': 'center','fontWeight': 'bold','font-size': "100%", 'color':'white'}
                            )#Granular Level cards
                        # Line plot body
                        ,dbc.Card(body = True,style = {'textAlign':'center','color':'white' },children=[
                            dbc.Row([
                                dbc.Col([html.P(id="mNN", className="card-title"),
                                         dcc.Graph(id = 'mDD',config = {'displayModeBar': False})]),
                                dbc.Col([html.P("Confirmed Cases", className="card-title"),
                                         dcc.Graph(id = 'mTP',config = {'displayModeBar': False})])
                                ])
                            ,html.Br()
                            ,dbc.Row([
                                dbc.Col([html.P("New Cases", className="card-title"),
                                         dcc.Graph(id = 'mNP',config = {'displayModeBar': False})]),
                                dbc.Col([html.P("Active Cases", className="card-title"),
                                         dcc.Graph(id = 'mAP',config = {'displayModeBar': False})])
                                ])
                            ,html.Br()
                            ,dbc.Row([
                                dbc.Col([html.P("Recovered", className="card-title"),
                                         dcc.Graph(id = 'mRP',config = {'displayModeBar': False})]),
                                dbc.Col([html.P("Deaths", className="card-title"),
                                         dcc.Graph(id = 'mDP',config = {'displayModeBar': False})])
                                ])
                            ])# Line plot body
                ###############################        
                        ]),# India Tab
                #World Tab
                dbc.Tab(label = "World",  tabClassName="mr-auto",children =[
                ###############################
                    #Total Level cards
                        dbc.CardGroup([
                            dbc.Card([
                                    html.P("Confirmed Cases",className="card-text")
                                    ,html.P(WTC, className="card-title")
                                    ]
                                    , color="primary", body = True),
                            dbc.Card([
                                    html.P("New Cases",className="card-text")
                                    ,html.P(WNC, className="card-title")
                                    ]
                                    , color="warning", body=True),
                            dbc.Card([
                                    html.P("Active Cases",className="card-text")
                                    ,html.P(WAC, className="card-title")
                                    ]
                                    , color="info", body=True),
                            dbc.Card([
                                    html.P("Recovered",className="card-text")
                                    ,html.P(WRE, className="card-title")
                                    ]
                                    , color="success", body=True),
                            dbc.Card([
                                    html.P("Deaths",className="card-text")
                                    ,html.P(WDT, className="card-title")
                                    ]
                                    , color="danger", body=True)
                            ]
                            ,style={'textAlign': 'center','fontWeight': 'bold','font-size': "160%", 'color':'white'}
                            )#Total Level cards
                        # Map body
                        ,dbc.Card(body = True, children = [
                            dbc.Row([
                                dbc.Col(width = 1),
                                dbc.Col(width = 10,children =[
                                    dbc.Tabs(id = "wMainTab",children=[
                                        dbc.Tab(label = "Confirmed Case",tabClassName="ml-auto",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(Wdt, LLw, JSw, 'TotalCases',2), width = '100%', height = '370')]
                                                ),
                                        dbc.Tab(label = "New Case",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(Wdt, LLw, JSw, 'NewCases',2), width = '100%', height = '370')]
                                                ),
                                        dbc.Tab(label = "Active Case",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(Wdt, LLw, JSw, 'ActiveCases',2), width = '100%', height = '370')]
                                                ),
                                        dbc.Tab(label = "Recovered",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(Wdt, LLw, JSw, 'Recovered',2), width = '100%', height = '370')]
                                                ),        
                                        dbc.Tab(label = "Death",
                                                children = [html.Iframe(srcDoc = CreateMapPlot(Wdt, LLw, JSw, 'Death',2), width = '100%', height = '370')]
                                                ),
                                        dbc.Tab(label = "Data",tabClassName="mr-auto",children = [
                                            dbc.Card(body = True, style={'height':'100%', 'width':'370'}, children=[
                                                dash_table.DataTable(
                                                        #id='table',
                                                        columns=[{"name": i, "id": i} for i in wdf.columns],
                                                        data=wdf.to_dict('records'),
                                                        style_cell={'textAlign': 'Center','width': '80px','fontSize':12},
                                                        style_table={'maxHeight': '370px','overflowY':'scroll'},
                                                        fixed_rows={ 'headers': True, 'data': 0 },
                                          #              style_as_list_view=True,
                                                        style_cell_conditional=[
                                                            {'if': {'column_id': "Sl.No"},
                                                                'backgroundColor': '#6c757d',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            } ,
                                                            {'if': {'column_id': 'Name'},
                                                                'backgroundColor': '#6c757d',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            } ,
                                                            {'if': {'column_id': 'No Cases Since'},
                                                                'backgroundColor': '#6c757d',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            } ,
                                                            {'if': {'column_id': 'Confirmed'},
                                                                'backgroundColor': '#01A9DB',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            },
                                                            {'if': {'column_id': 'New'},
                                                                'backgroundColor': '#FF8000',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            },
                                                            {'if': {'column_id': 'Active'},
                                                                'backgroundColor': '#9F81F7',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            },
                                                            {'if': {'column_id': 'Recovered'},
                                                                'backgroundColor': '#28a745',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            },
                                                            {'if': {'column_id': 'Deaths'},
                                                                'backgroundColor': '#dc3545',
                                                                'color': 'white',
                                                                'fontWeight': 'bold'
                                                            }
                                                            
                                                          ]
                                                        )
                                                ])
                                            ])
                                        ])
                                    ]),
                                dbc.Col(width = 1),
                                ])
                            ])# Map body
                        ,html.Br()
                        #granular drop down
                        ,dbc.Row([
                            dbc.Col(["Select Country - "], width = 4,style = {'textAlign':'right','fontWeight': 'bold'}),
                            dbc.Col(width = 4, children=[
                                dcc.Dropdown(
                                        id='wdd',
                                        options=[{'label':cl, 'value':cl} for cl in list(sorted(wdf.Name.unique()))],
                                        value = 'India',
                                        clearable=False,
                                        placeholder="Select a Country"
                                        #,style={'font-size': "110%"}#'height': '2px', 'width': '100px', 'font-size': "50%",'min-height': '1px' }
                                    )
                                ]),
                            dbc.Col(width = 4)
                            ])#granular drop down
                        ,html.Br()
                        #Granular Level cards
                        ,dbc.CardGroup([
                            dbc.Card([
                                    html.P("Confirmed Cases",className="card-text")
                                    ,html.P(id = 'wTC', className="card-title")
                                    ]
                                    , color="primary", body = True),
                            dbc.Card([
                                    html.P("New Cases",className="card-text")
                                    ,html.P(id = 'wNC', className="card-title")
                                    ]
                                    , color="warning", body=True),
                            dbc.Card([
                                    html.P("Active Cases",className="card-text")
                                    ,html.P(id = 'wAC', className="card-title")
                                    ]
                                    , color="info", body=True),
                            dbc.Card([
                                    html.P("Recovered",className="card-text")
                                    ,html.P(id = 'wRC', className="card-title")
                                    ]
                                    , color="success", body=True),
                            dbc.Card([
                                    html.P("Deaths",className="card-text")
                                    ,html.P(id = 'wDC', className="card-title")
                                    ]
                                    , color="danger", body=True)
                            ]
                            ,style={'textAlign': 'center','fontWeight': 'bold','font-size': "100%", 'color':'white'}
                            )#Granular Level cards
                        # Line plot body
                        ,dbc.Card(body = True,style = {'textAlign':'center','color':'white'},children=[
                            dbc.Row([
                                dbc.Col([html.P(id="wNN", className="card-title"),
                                         dcc.Graph(id = 'wDD',config = {'displayModeBar': False})]),
                                dbc.Col([html.P("Confirmed Cases", className="card-title"),
                                         dcc.Graph(id = 'wTP',config = {'displayModeBar': False})])
                                ])
                            ,html.Br()
                            ,dbc.Row([
                                dbc.Col([html.P("New Cases", className="card-title"),
                                         dcc.Graph(id = 'wNP',config = {'displayModeBar': False})]),
                                dbc.Col([html.P("Active Cases", className="card-title"),
                                         dcc.Graph(id = 'wAP',config = {'displayModeBar': False})])
                                ])
                            ,html.Br()
                            ,dbc.Row([
                                dbc.Col([html.P("Recovered", className="card-title"),
                                         dcc.Graph(id = 'wRP',config = {'displayModeBar': False})]),
                                dbc.Col([html.P("Deaths", className="card-title"),
                                         dcc.Graph(id = 'wDP',config = {'displayModeBar': False})])
                                ])
                            ])# Line plot body                        
                ###############################                
                        ])#World Tab
                ])#Main Tab Item
            
            
            
            ])#Main Body

    ])
        


app = dash.Dash(__name__,
                #external_scripts=external_scripts,
                external_stylesheets=[dbc.themes.CYBORG])
server = app.server
app.title="COVID-19"
app.layout = create_layout(data_path)


############## Callbacks ############
@app.callback(
    [Output('mTC','children'),
     Output('mNC','children'),
     Output('mAC','children'),
     Output('mRC','children'),
     Output('mDC','children')],
    [Input('dd','value')]
    )
def state_box_vaues(value):
    mdt2 = mdt[mdt.Name_1 == value]
    TC1 = sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'TotalCases'])
    TC = '{:,.0f}'.format(TC1)
    NC = '{:,.0f}'.format(sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'NewCases']))
    AC = sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'ActiveCases'])
    AC = '{:,.0f}'.format(AC)+" ("+str(round((AC/TC1)*100,2))+"%)"
    RE = sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'Recovered'])
    RE = '{:,.0f}'.format(RE)+" ("+str(round((RE/TC1)*100,2))+"%)"
    DT = sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'Death'])
    DT = '{:,.0f}'.format(DT)+" ("+str(round((DT/TC1)*100,2))+"%)"
    return TC, NC, AC, RE, DT
    
@app.callback(
    [Output('mTP','figure'),
     Output('mNP','figure'),
     Output('mAP','figure'),
     Output('mRP','figure'),
     Output('mDP','figure'),
     Output('mDD','figure'),
     Output('mNN','children')],
    [Input('dd','value')]
    )
def state_chart_plots(value):
    list = ['TotalCases', 'NewCases',"ActiveCases", "Recovered", "Death"]
    #var = list[0]
    fdf ={}
    for var in list:
        df2 = mdt[['Date','Name_1', var]]
        df3=df2.pivot(index='Date', columns='Name_1', values=var)
        df3 = df3.replace(np.nan,0)
        df3['India']= df3.sum(axis=1)
        #df3 = df3.assign(var_nm = str(var))
        fdf.update({var : df3})
    
    TC = generateplot(value,'TotalCases',fdf,1)
    NC = generateplot(value,'NewCases',fdf,1)
    AC = generateplot(value,'ActiveCases',fdf,1)
    RC = generateplot(value,'Recovered',fdf,1)
    DC = generateplot(value,'Death',fdf,1)
    
    df = mdt[mdt.Name_1 == value]
    df.reset_index(drop=True, inplace=True)
    df = df[['Date','Name_1', 'TotalCases', 'NewCases',"ActiveCases", "Recovered", "Death"]]
    df.columns = ['Date','Name', 'Confirmed', 'New',"Active", "Recovered", "Deaths"]
    
    fig = go.Figure()
    clr = ['blue', 'orange', 'purple', 'green','red']
    vars = ['Confirmed', 'New',"Active", "Recovered", "Deaths"]
    annotations = []
    for i in range(0,5):
        fig.add_trace(go.Scatter(x=df.Date, y=df[vars[i]], name=vars[i],
                             line = dict(color= clr[i])))
        annotations.append(dict(xref='paper', x=1, y=df[vars[i]][len(df)-1],
                             xanchor='left', yanchor='middle',
                             text= vars[i],
                             font=dict(color = clr[i]),
                             showarrow=False))
    
    fig.update_layout(showlegend=False,annotations=annotations,margin=dict(t=10,b=10,l=10,pad=2),height=150)
    print("State plot completed..")
    return TC, NC, AC, RC, DC, fig, value
@app.callback(
    [Output('wTC','children'),
     Output('wNC','children'),
     Output('wAC','children'),
     Output('wRC','children'),
     Output('wDC','children')],
    [Input('wdd','value')]
    )
def country_box_vaues(value):
    mdt2 = Wdt[Wdt.Name_1 == value]
    TC1 = sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'TotalCases'])
    TC = '{:,.0f}'.format(TC1)
    NC = '{:,.0f}'.format(sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'NewCases']))
    AC = sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'ActiveCases'])
    AC = '{:,.0f}'.format(AC)+" ("+str(round((AC/TC1)*100,2))+"%)"
    RE = sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'Recovered'])
    RE = '{:,.0f}'.format(RE)+" ("+str(round((RE/TC1)*100,2))+"%)"
    DT = sum(mdt2.loc[mdt2.Date==max(mdt2.Date),'Death'])
    DT = '{:,.0f}'.format(DT)+" ("+str(round((DT/TC1)*100,2))+"%)"
    return TC, NC, AC, RE, DT
    
@app.callback(
    [Output('wTP','figure'),
     Output('wNP','figure'),
     Output('wAP','figure'),
     Output('wRP','figure'),
     Output('wDP','figure'),
     Output('wDD','figure'),
     Output('wNN','children')],
    [Input('wdd','value')]
    )
def country_chart_plots(value):
    list = ['TotalCases', 'NewCases',"ActiveCases", "Recovered", "Death"]
    #var = list[0]
    fdf ={}
    for var in list:
        df2 = Wdt[['Date','Name_1', var]]
        df3=df2.pivot(index='Date', columns='Name_1', values=var)
        df3 = df3.replace(np.nan,0)
        df3['World']= df3.sum(axis=1)
        #df3 = df3.assign(var_nm = str(var))
        fdf.update({var : df3})
    
    TC = generateplot(value,'TotalCases',fdf,2)
    NC = generateplot(value,'NewCases',fdf,2)
    AC = generateplot(value,'ActiveCases',fdf,2)
    RC = generateplot(value,'Recovered',fdf,2)
    DC = generateplot(value,'Death',fdf,2)
    
    df = Wdt[Wdt.Name_1 == value]
    df.reset_index(drop=True, inplace=True)
    df = df[['Date','Name_1', 'TotalCases', 'NewCases',"ActiveCases", "Recovered", "Death"]]
    df.columns = ['Date','Name', 'Confirmed', 'New',"Active", "Recovered", "Deaths"]
    
    fig = go.Figure()
    clr = ['blue', 'orange', 'purple', 'green','red']
    vars = ['Confirmed', 'New',"Active", "Recovered", "Deaths"]
    annotations = []
    for i in range(0,5):
        fig.add_trace(go.Scatter(x=df.Date, y=df[vars[i]], name=vars[i],
                             line = dict(color= clr[i])))
        annotations.append(dict(xref='paper', x=1, y=df[vars[i]][len(df)-1],
                             xanchor='left', yanchor='middle',
                             text= vars[i],
                             font=dict(color = clr[i]),
                             showarrow=False))
        
    fig.update_layout(showlegend=False,annotations=annotations,margin=dict(t=10,b=10,l=10,pad=2),height=150
                      ,
                      #paper_bgcolor='rgba(255,255,255,0.5)',
                      #plot_bgcolor='rgba(0,0,0,0)',
                      #font = dict(color = "#fafafa")
                      )
    print("Country plot completed..")
    return TC, NC, AC, RC, DC, fig, value

   
if __name__ == '__main__':
    app.run_server(debug=False)

