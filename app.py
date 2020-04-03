# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# Create Dash dashboard
# Last Updated - 03/16/2020  - 04/01/2020

#import os
#os.getcwd()
#os.path
import sys
#sys.path.insert(1,'D:\PythonPackages')
#sys.path.insert(2,'D:\PythonPractice\WebScrapper')
#print(sys.path)

#import os
#import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import numpy as np
#import time
#from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
#os.system("WebScrapper.py 1")
#import WebScrapper3  as WS


# data path
data_path = "https://github.com/pratik-bose/CoronaTracker/"
# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

colors = {
    'background': '#111111',
    'text': '#FAF7F4'
}



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


def serve_layout():
#from WebScrapper3 import DtaScrapper
    global Wdt, mdt
    
    Wdt = pd.read_csv(str(data_path) + 'WorldCoronaData.csv')
    mdt = pd.read_csv(str(data_path) + 'CoronaData.csv')
    print('Data load complete..')
    
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
    DT_TM = str(max(mdt.Date)+':'+TM)
    
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
    WDT_TM = str(max(Wdt.Date)+':'+WTM)

########### Total Plot ################
    def totalplot(mdt,id):
        if id == 1:
            contname = 'india_plot_container'
        elif id == 2:
            contname = 'world_plot_container'
        
        dff = mdt.groupby(['Date']).agg({  'TotalCases' :sum,
                                           'NewCases': sum,
                                           'ActiveCases': sum,
                                           'Recovered':sum,
                                           'Death':sum
                                       })
        
        dt = pd.DataFrame(sorted(mdt.Date.unique()),columns = ['Date'])
        dff = pd.merge(dt, dff, on='Date', how='left')
        dff = dff.replace(np.nan,0)
        
        fig = make_subplots(rows=5, cols=1, shared_xaxes=True,
                                vertical_spacing=0.1,horizontal_spacing=0.1)
        fig.append_trace({'x':dff.Date,'y':dff.TotalCases,'type':'bar',"marker": {"color": "#007bff"},'name':'Total Cases'},1,1)
        fig.append_trace({'x':dff.Date,'y':dff.NewCases,'type':'bar',"marker": {"color": "#ffc107"},'name':'New Cases'},2,1)
        fig.append_trace({'x':dff.Date,'y':dff.ActiveCases,'type':'bar',"marker": {"color": "#17a2b8"},'name':'Active Cases'},3,1)
        fig.append_trace({'x':dff.Date,'y':dff.Recovered,'type':'bar',"marker": {"color": "#28a745"},'name':'Total Recovered'},4,1)
        fig.append_trace({'x':dff.Date,'y':dff.Death,'type':'bar',"marker": {"color": "#dc3545"},'name':'Total Death'},5,1)
        #fig.update_layout(legend_orientation="h",legend = dict(x=0.5, y=1.2),margin=dict(t=5,l=0,r=5))
        
        fig.update_layout(showlegend=False,margin=dict(t=0,l=0,r=5,b=0,pad=4),width=290,height=400)
        return html.Div(dcc.Graph(id=contname,figure = fig,config = {'displayModeBar': False}))



    height = 400
    width = 300
    print('Creating Layout..')
    
#### Define Layout ####
    return html.Div([
        #Navigation Bar
        dbc.NavbarSimple(#style={'font-size': "150%"}#,'height': '15px'}#, 'width': '100px', 'min-height': '1px' }
            children=[
                    dbc.Row([
                            dbc.Col(
                            dbc.DropdownMenu(
                            children=[
                                    dbc.DropdownMenuItem("Data Sources", header=True),
                                    dbc.DropdownMenuItem(divider=True),
                                    dbc.DropdownMenuItem("1) Ministry of Health and Family Welfare, India", href="https://www.mohfw.gov.in/"),
                                    dbc.DropdownMenuItem("2) Worldometer", href="https://www.worldometers.info/"),
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
                                        "Created by Pratik Bose on 01-04-2020"
                                        ,className="text-muted px-4 mt-4",
                                    )
                    
                
                                ],
                            nav=True,
                            in_navbar=True,
                            label="More",
                            style={'font-size': "150%",'align':'center'}#,'height': '15px'}#, 'width': '100px', 'min-height': '1px' }
                            ),width = 'auto'),
                            dbc.Col(html.I(className="fas fa-chevron-down mr-2"),width = 'auto')
                    ],
                    no_gutters=True,
                    className="my-1"
                    )
           ],
                brand="Coronavirus COVID-19 Cases",
                color="primary",
                dark=True,
            )#Navigation Bar
        #Main Body
        ,html.Div([
        #Main Tabs
        dbc.Tabs(id="tabs",# value='TabIndia',
                 children=[
                    dbc.Tab(label='India',labelClassName="text-success",tabClassName="ml-auto",
                            children = [
                                    html.Br(),
                                    dbc.Row(children=[
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total Confirmed Cases",className="card-text")
                                                             ,html.H1(TC, className="card-title")
                                                             ]
                                                             , color="primary", body = True)),
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total New Cases",className="card-text")
                                                             ,html.H1(NC, className="card-title")
                                                             ]
                                                             , color="warning", body=True)),
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total Active Cases",className="card-text")
                                                             ,html.H1(AC, className="card-title")
                                                             ]
                                                             , color="info", body=True)),
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total Recovered",className="card-text")
                                                             ,html.H1(RE, className="card-title")
                                                             ]
                                                             , color="success", body=True)),
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total Deaths",className="card-text")
                                                             ,html.H1(DT, className="card-title")
                                                             ]
                                                             , color="danger", body=True))
                                            ]
                                            ,style={'textAlign': 'center','color': colors['text']}
                                            ),
                                    dbc.Card(body = True,children = [dbc.Row(children = [
                                            #Sidebar Left
                                            dbc.Col(children = [
                                                    dbc.Card(
                                                            dbc.CardBody([
                                                                    html.Br(),
                                                                    html.H4(html.Div("COVID-19 INDIA Cases"),style={'textAlign': 'center'}),
                                                                    #html.Div(id = 'deathcasesplot')
                                                                    html.Div(id = 'indiaplot',style={'oveflowY':'scroll','width': width,'height':height},children=[totalplot(mdt,1)])
                                                                    ])#Sidebarcard Body
                                                             ) #Sidebarcard
                                                    ],width = 3)#Sidebar Left
                                            #Body
                                            ,dbc.Col(children = [
                                                    dbc.Card(
                                                            dbc.CardBody([
                                                                    dcc.Tabs(id = "MainTab",value = "tab1",children=[
                                                                            dcc.Tab(label = "Confirmed Case",value = "tab1", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'TotalCases.html').read(), width = '100%', height = '400')]
                                                                                    ),
                                                                            dcc.Tab(label = "New Case",value = "tab2", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'NewCases.html').read(), width = '100%', height = '400')]
                                                                                    ),
                                                                            dcc.Tab(label = "Active Case",value = "tab3", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'ActiveCases.html').read(), width = '100%', height = '400')]
                                                                                    ),
                                                                            dcc.Tab(label = "Recovered",value = "tab4", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'Recovered.html').read(), width = '100%', height = '400')]
                                                                                    ),        
                                                                            dcc.Tab(label = "Death",value = "tab5", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'Death.html').read(), width = '100%', height = '400')]
                                                                                    )        
                                                                            ])
                                                                ])#Bodycard Body
                                                    ),
                                                    dbc.Card(body = True,children =[
                                                            dbc.Row([
                                                                    dbc.Col([html.Div(["Total affected States & UTs : " + str(len(mdt.State_1.unique()))])],width = 6),
                                                                    dbc.Col([html.Div(["Data last fetched on : " + DT_TM])],width = 6)
                                                                    ])
                                                            
                                                            ],style={'backgroundColor': colors['background'],'textAlign': 'center','color': colors['text']})                        
                                                    ],width = 6),#Body
                                            #Sidebar Right
                                            dbc.Col(children = [
                                                    dbc.Card(
                                                            dbc.CardBody([
                                                                    dbc.Row(children = [
                                                                            dbc.Col([html.Br(),html.H4(html.Div("Select State"))],width=5),
                                                                            dbc.Col([dcc.Dropdown(
                                                                                    id='dd',
                                                                                    options=[{'label':cl, 'value':cl} for cl in list(sorted(mdt.State_1.unique()))],
                                                                                    value = 'West Bengal'
                                                                                    ,style={'font-size': "110%"}#'height': '2px', 'width': '100px', 'font-size': "50%",'min-height': '1px' }
                                                                                    )],width=7)
                                                                    ]),
                                                                    #html.H4(html.Div("Sate Summary")),
                                                                    dbc.Row([
                                                                             dbc.Col([
                                                                                      dbc.Button(id = "mTC", color="primary",style={'width': '100%'}),html.Br(),
                                                                                      html.Br(),html.Br(),html.Br(),dbc.Button(id = "mNC", color="warning",style={'width': '100%'}),html.Br(),
                                                                                      html.Br(),html.Br(),html.Br(),dbc.Button(id = "mAC", color="info",style={'width': '100%'}),html.Br(),
                                                                                      html.Br(),html.Br(),html.Br(),dbc.Button(id = "mRC", color="success",style={'width': '100%'}),html.Br(),
                                                                                      html.Br(),html.Br(),html.Br(),dbc.Button(id = "mDC", color="danger",style={'width': '100%'}),html.Br(),
                                                                                     ],width = 4),
                                                                             dbc.Col([html.Div(id = 'stateplot',style={'oveflowY':'scroll','width': width,'height':height})],width = 8)
                                                                             ],style={'textAlign': 'center','color': colors['text']}
                                                                     )
                                                                    ])#Sidebarcard Body
                                                             ) #Sidebarcard
                                                    ],width = 3)#Sidebar Right    
                                           ])])#Main Card
                                    ])#Tab India
                    ,dbc.Tab(label='World',labelClassName="text-primary",#tabClassName="ml-auto",
                            children =[
                                    html.Br(),
                                    dbc.Row(children=[
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total Confirmed Cases",className="card-text")
                                                             ,html.H1(WTC, className="card-title")
                                                             ]
                                                             , color="primary", body = True)),
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total New Cases",className="card-text")
                                                             ,html.H1(WNC, className="card-title")
                                                             ]
                                                             , color="warning", body=True)),
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total Active Cases",className="card-text")
                                                             ,html.H1(WAC, className="card-title")
                                                             ]
                                                             , color="info", body=True)),
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total Recovered",className="card-text")
                                                             ,html.H1(WRE, className="card-title")
                                                             ]
                                                             , color="success", body=True)),
                                            dbc.Col(dbc.Card([
                                                             html.H3("Total Deaths",className="card-text")
                                                             ,html.H1(WDT, className="card-title")
                                                             ]
                                                             , color="danger", body=True))
                                            ]
                                            ,style={'textAlign': 'center','color': colors['text']}
                                            ),
                                    dbc.Card(body = True,children = [dbc.Row(children = [
                                            #Sidebar Left
                                            dbc.Col(children = [
                                                    dbc.Card(
                                                            dbc.CardBody([
                                                                    html.Br(),
                                                                    html.H4(html.Div("COVID-19 World Cases"),style={'textAlign': 'center'}),
                                                                    #html.Div(id = 'deathcasesplot')
                                                                    html.Div(id = 'Tworldplot',style={'oveflowY':'scroll','width': width,'height':height},children=[totalplot(Wdt,2)])
                                                                    ])#Sidebarcard Body
                                                             ) #Sidebarcard
                                                    ],width = 3)#Sidebar Left
                                            #Body
                                            ,dbc.Col(children = [
                                                    dbc.Card(
                                                            dbc.CardBody([
                                                                    dcc.Tabs(id = "WMainTab",value = "Wtab1",children=[
                                                                            dcc.Tab(label = "Confirmed Case",value = "Wtab1", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'World_TotalCases.html').read(), width = '100%', height = '400')]
                                                                                    ),
                                                                            dcc.Tab(label = "New Case",value = "Wtab2", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'World_NewCases.html').read(), width = '100%', height = '400')]
                                                                                    ),
                                                                            dcc.Tab(label = "Active Case",value = "Wtab3", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'World_ActiveCases.html').read(), width = '100%', height = '400')]
                                                                                    ),
                                                                            dcc.Tab(label = "Recovered",value = "Wtab4", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'World_Recovered.html').read(), width = '100%', height = '400')]
                                                                                    ),        
                                                                            dcc.Tab(label = "Death",value = "Wtab5", style=tab_style, selected_style=tab_selected_style,
                                                                                    children = [html.Iframe(srcDoc = open(str(data_path) + 'World_Death.html').read(), width = '100%', height = '400')]
                                                                                    )        
                                                                            ])
                                                                ])#Bodycard Body
                                                    ),
                                                    dbc.Card(body = True,children =[
                                                            dbc.Row([
                                                                    dbc.Col([html.Div(["Total affected Countries & Territories : " + str(len(Wdt.Country_1.unique()))])],width = 6),
                                                                    dbc.Col([html.Div(["Data last fetched on : " + WDT_TM])],width = 6)
                                                                    ])
                                                            
                                                            ],style={'backgroundColor': colors['background'],'textAlign': 'center','color': colors['text']})                        
                                                    ],width = 6),#Body
                                            #Sidebar Right
                                            dbc.Col(children = [
                                                    dbc.Card(
                                                            dbc.CardBody([
                                                                    dbc.Row(children = [
                                                                            dbc.Col([html.Br(),html.H4(html.Div("Select Country"))],width=5),
                                                                            dbc.Col([dcc.Dropdown(
                                                                                    id='Wdd',
                                                                                    options=[{'label':cl, 'value':cl} for cl in list(sorted(Wdt.Country_1.unique()))],
                                                                                    value = 'India'
                                                                                    ,style={'font-size': "110%"}#'height': '2px', 'width': '100px', 'font-size': "50%",'min-height': '1px' }
                                                                                    )],width=7)
                                                                    ]),
                                                                    #html.H4(html.Div("Sate Summary")),
                                                                    #html.Div(id = 'deathcasesplot')
                                                                    dbc.Row([
                                                                             dbc.Col([
                                                                                      dbc.Button(id = "WTC", color="primary",style={'width': '100%'}),html.Br(),
                                                                                      html.Br(),html.Br(),html.Br(),dbc.Button(id = "WNC", color="warning",style={'width': '100%'}),html.Br(),
                                                                                      html.Br(),html.Br(),html.Br(),dbc.Button(id = "WAC", color="info",style={'width': '100%'}),html.Br(),
                                                                                      html.Br(),html.Br(),html.Br(),dbc.Button(id = "WRC", color="success",style={'width': '100%'}),html.Br(),
                                                                                      html.Br(),html.Br(),html.Br(),dbc.Button(id = "WDC", color="danger",style={'width': '100%'}),html.Br(),
                                                                                     ],width = 4),
                                                                             dbc.Col([html.Div(id = 'worldplot',style={'oveflowY':'scroll','width': width,'height':height})],width = 8)
                                                                             ],style={'textAlign': 'center','color': colors['text']}
                                                                     )
                                                                    ])#Sidebarcard Body
                                                             ) #Sidebarcard
                                                    ],width = 3)#Sidebar Right    
                                           ])])#Main Card
                                    ])#Tab World
                 ],
                 style={
                'width': '50%',
                'font-size': '200%',
                'height':'5vh'
                })#Main Tab
            ])#Main Body 
        ])# app/layout
    

app = dash.Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)
    
app.layout = serve_layout

print('Layout complete..')    
########### State Plot ################
@app.callback(
            Output('stateplot','children'),
            [Input('dd','value')]
        )
def stateplot(value):
    dt = pd.DataFrame(sorted(mdt.Date.unique()),columns = ['Date'])
    dff = mdt.loc[mdt.State_1 == value,['Date','State_1','TotalCases','NewCases','ActiveCases','Recovered','Death']]
    dff = pd.merge(dt, dff, on='Date', how='left')
    dff = dff.replace(np.nan,0)
    
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,horizontal_spacing=0.1)
    
    
    fig.append_trace({'x':dff.Date,'y':dff.TotalCases,'type':'bar',"marker": {"color": "#007bff"},'name':'Total Cases'},1,1)
    fig.append_trace({'x':dff.Date,'y':dff.NewCases,'type':'bar',"marker": {"color": "#ffc107"},'name':'New Cases'},2,1)
    fig.append_trace({'x':dff.Date,'y':dff.ActiveCases,'type':'bar',"marker": {"color": "#17a2b8"},'name':'Active Cases'},3,1)
    fig.append_trace({'x':dff.Date,'y':dff.Recovered,'type':'bar',"marker": {"color": "#28a745"},'name':'Total Recovered'},4,1)
    fig.append_trace({'x':dff.Date,'y':dff.Death,'type':'bar',"marker": {"color": "#dc3545"},'name':'Total Death'},5,1)
    
    #fig.update_layout(legend_orientation="h",legend = dict(x=0.25, y=1.2),margin=dict(t=0,l=0,r=1))
    fig.update_layout(showlegend=False,margin=dict(t=0,l=0,r=5,b=0,pad=4),width=175,height=400)

                                                                         
    return html.Div(dcc.Graph(id='state_plot_container',figure = fig,config = {'displayModeBar': False}))
    
####### Buttons##############
@app.callback(
            Output('mTC','children'),
            [Input('dd','value')]
        )
def ButtonmTC(value):
    dff = mdt.loc[mdt.Date == max(mdt.Date),]
    dff = int(dff.loc[dff.State_1 == value,'TotalCases'])
    return(html.H4('{:,.0f}'.format(dff)))

@app.callback(
            Output('mNC','children'),
            [Input('dd','value')]
        )
def ButtonmNC(value):
    dff = mdt.loc[mdt.Date == max(mdt.Date),]
    dff = int(dff.loc[dff.State_1 == value,'NewCases'])
    return(html.H4('{:,.0f}'.format(dff)))
@app.callback(
            Output('mAC','children'),
            [Input('dd','value')]
        )
def ButtonmAC(value):
    dff = mdt.loc[mdt.Date == max(mdt.Date),]
    dff = int(dff.loc[dff.State_1 == value,'ActiveCases'])
    return(html.H4('{:,.0f}'.format(dff)))
@app.callback(
            Output('mRC','children'),
            [Input('dd','value')]
        )
def ButtonmRC(value):
    dff = mdt.loc[mdt.Date == max(mdt.Date),]
    dff = int(dff.loc[dff.State_1 == value,'Recovered'])
    return(html.H4('{:,.0f}'.format(dff)))
@app.callback(
            Output('mDC','children'),
            [Input('dd','value')]
        )
def ButtonmDC(value):
    dff = mdt.loc[mdt.Date == max(mdt.Date),]
    dff = int(dff.loc[dff.State_1 == value,'Death'])
    return(html.H4('{:,.0f}'.format(dff)))

########### World Plot ################
@app.callback(
            Output('worldplot','children'),
            [Input('Wdd','value')]
        )
def worldplot(value):
    dt = pd.DataFrame(sorted(Wdt.Date.unique()),columns = ['Date'])
    dff = Wdt.loc[Wdt.Country_1 == value,['Date','Country_1','TotalCases','NewCases','ActiveCases','Recovered','Death']]
    dff = pd.merge(dt, dff, on='Date', how='left')
    dff = dff.replace(np.nan,0)
    
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,horizontal_spacing=0.1)
    
    
    fig.append_trace({'x':dff.Date,'y':dff.TotalCases,'type':'bar',"marker": {"color": "#007bff"},'name':'Total Cases'},1,1)
    fig.append_trace({'x':dff.Date,'y':dff.NewCases,'type':'bar',"marker": {"color": "#ffc107"},'name':'New Cases'},2,1)
    fig.append_trace({'x':dff.Date,'y':dff.ActiveCases,'type':'bar',"marker": {"color": "#17a2b8"},'name':'Active Cases'},3,1)
    fig.append_trace({'x':dff.Date,'y':dff.Recovered,'type':'bar',"marker": {"color": "#28a745"},'name':'Total Recovered'},4,1)
    fig.append_trace({'x':dff.Date,'y':dff.Death,'type':'bar',"marker": {"color": "#dc3545"},'name':'Total Death'},5,1)
    
    #fig.update_layout(legend_orientation="h",legend = dict(x=0.25, y=1.2),margin=dict(t=0,l=0,r=1))
    fig.update_layout(showlegend=False,margin=dict(t=0,l=0,r=5,b=0,pad=4),width=175,height=400)

                                                                         
    return html.Div(dcc.Graph(id='country_plot_container',figure = fig,config = {'displayModeBar': False}))

####### Buttons##############
@app.callback(
            Output('WTC','children'),
            [Input('Wdd','value')]
        )
def ButtonWTC(value):
    dff = Wdt.loc[Wdt.Date == max(Wdt.Date),]
    dff = int(dff.loc[dff.Country_1 == value,'TotalCases'])
    return(html.H4('{:,.0f}'.format(dff)))
@app.callback(
            Output('WNC','children'),
            [Input('Wdd','value')]
        )
def ButtonWNC(value):
    dff = Wdt.loc[Wdt.Date == max(Wdt.Date),]
    dff = int(dff.loc[dff.Country_1 == value,'NewCases'])
    return(html.H4('{:,.0f}'.format(dff)))
@app.callback(
            Output('WAC','children'),
            [Input('Wdd','value')]
        )
def ButtonWAC(value):
    dff = Wdt.loc[Wdt.Date == max(Wdt.Date),]
    dff = int(dff.loc[dff.Country_1 == value,'ActiveCases'])
    return(html.H4('{:,.0f}'.format(dff)))
@app.callback(
            Output('WRC','children'),
            [Input('Wdd','value')]
        )
def ButtonWRC(value):
    dff = Wdt.loc[Wdt.Date == max(Wdt.Date),]
    dff = int(dff.loc[dff.Country_1 == value,'Recovered'])
    return(html.H4('{:,.0f}'.format(dff)))    
@app.callback(
            Output('WDC','children'),
            [Input('Wdd','value')]
        )
def ButtonWDC(value):
    dff = Wdt.loc[Wdt.Date == max(Wdt.Date),]
    dff = int(dff.loc[dff.Country_1 == value,'Death'])
    return(html.H4('{:,.0f}'.format(dff)))

if __name__ == '__main__':
    app.run_server(debug=True)
    
'''
use dbc.row and dbc.col instead
'''
