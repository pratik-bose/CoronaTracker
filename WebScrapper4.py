# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 15:50:43 2020

@author: 1247392
"""

import sys
sys.path.insert(1,'D:\PythonPackages')

import requests
import lxml.html as lh
import pandas as pd
from datetime import datetime
import numpy as np
import folium
import webbrowser
import os
import json
from folium.plugins import MarkerCluster
import time
#from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
data_path = "D:\PythonPractice\WebScrapper\\"
#url = 'https://en.wikipedia.org/wiki/Template:2019%E2%80%9320_coronavirus_pandemic_data/India_medical_cases'
url = 'https://www.mohfw.gov.in/'

def DataScrapper(url=url,req_plot = False,plot_type = 2):
    #Create a handle, page, to handle the contents of the website
    page = requests.get(url)
    #Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    #Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')
    #Check the length of the first 12 rows
    col_len = max([len(T) for T in tr_elements])
    #col_len = 6
    col_list = [len(T) == col_len for T in tr_elements]
    
    new_list = []
    for i in range(0,len(tr_elements)):
        if col_list[i] == True:
            new_list.append(tr_elements[i])
  
          
    #Check
    if (max([len(T) for T in new_list]) != min([len(T) for T in new_list])):
        print('Table structure has changed. Cannot Proceed..')
        exit
        
    #Create empty list
    col=[]
    i=0
    #For each row, store each first element (header) and an empty list
    for t in new_list[0]: # starting from 2nd row for column headers
        i+=1
      #  if i == 4:
      #      continue
        name=t.text_content()
        col.append((name,[]))
        
    
    
    #Since out first row is the header, data is stored on the second row onwards
    for j in range(1,len(new_list)):
        #T is our j'th row
        T=new_list[j]
        
        #If row is not of size 10, the //tr data is not from our table 
        if len(T)!=col_len:
            break
        
        #i is the index of our column
        i=0
        k=0
        #Iterate through each element of the row
        for t in T.iterchildren():
            # Omit 3rd column
           # if i == 3:
            #    i +=1
             #   continue
            data=t.text_content() 
            #Check if row is empty
            if i>0:
            #Convert any numerical value to integers
                try:
                    data=int(data)
                except:
                    pass
            #Append the data to the empty list of the i'th column
            col[k][1].append(data)
            #Increment i for the next column
            i+=1
            k+=1
    #print(col)
    #close coonection with url
    page.connection.close()
    #[len(C) for (title,C) in col]
    
    Dict={title:column for (title,column) in col}
    df=pd.DataFrame(Dict)
    '''
    s = []
    for st in df.iloc[:,1]:
        #print(st)
        st = st.strip('\n')
        st = st.strip(' †\n')
        #print(st)
        s.append(st)
    
    df = df.assign(State_1 = s)
    '''
    #df = df.drop(df.columns[1], axis=1)
    df.columns = ['S. No.','State_1','TotalCases','Recovered','Death']
    df = df.assign(ActiveCases = df.TotalCases - (df.Recovered + df.Death))
    df = df[['S. No.','State_1','TotalCases','ActiveCases','Recovered','Death']]
    Date = datetime.now().strftime('%Y-%m-%d')
    Time = datetime.now().strftime('%H:%M:%S')
    df = df.assign(Date = Date)
    df = df.assign(Time = Time)
    
    print('Total Cases: ' + str(sum(df['TotalCases']))+' As of: '+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Load base data    
    mdt= pd.read_csv(str(data_path)+ 'CoronaData.csv')
    #Import Lat Long
    geo_data = pd.read_csv(str(data_path)+ 'GeoData.csv')
    #Import GeoJson file
    state_geo = str(data_path)+ 'Ind_geo.txt'
    with open(state_geo) as f:
        data = json.load(f)

        
    if(max(mdt['Date']) == Date):
        sdt = mdt[mdt['Date'] == Date]
        today = True
    else:
        sdt = mdt[mdt['Date'] == max(mdt['Date'])]
        sdt = sdt.assign(NewCases = 0)
        today = False

    NewCase = []
    CaseSince = []
    Geo = []
    for i in df['State_1']:
        #NewCase
        
        if len(sdt.loc[sdt['State_1'] == i,]) == 0 :
            continue
        
        TC_N = int(df.loc[df['State_1'] == i,'TotalCases']) 
        TC_O = int(sdt.loc[sdt['State_1'] == i,'TotalCases'])
        NC = TC_N - TC_O   
        NC_O = int(sdt.loc[sdt['State_1'] == i,'NewCases'])
        NewCase.append(NC_O + NC)
        
        #No new case since
        NNC_O = int(sdt.loc[sdt['State_1'] == i,'NoNewCasesSince'])
        if today == False:
            NNC = 0 if NC > 0 else NNC_O + 1
        else:
            NNC = 0 if NC > 0 else NNC_O
        
        CaseSince.append(NNC)
        Geo.append(i)
    
    
    new = pd.DataFrame({'State_1': Geo,
                       'NewCases' : NewCase,
                       'NoNewCasesSince' : CaseSince
                       })
    
    df = pd.merge(df, new, on='State_1', how='left')
    
    df = df.replace(np.nan,0)
    
    print('New cases for today - ',str(sum(df['NewCases'])))
    
    if today == True:
        mdt = mdt.loc[-(mdt['Date']==Date),]        
        mdt = mdt.append(df)
    else:
        mdt = mdt.append(df)
        
    #Write csv
    mdt.to_csv (str(data_path)+ 'CoronaData.csv', index = None, header=True)
    print('Data Updated...')
    
    # Create Visualisation
    df = pd.merge(df, geo_data, on='State_1', how='left')
    
    '''
    for i in range(0,len(df)):
            df.loc[i,'StateInfo'] = df.loc[i,'State_2'] \
                                    + ', Total - ' + str(df.loc[i,'TotalCases']) \
                                    +', New - ' + str(df.loc[i,'NewCases']) \
                                    +', Active - ' + str(df.loc[i,'ActiveCases']) \
                                    +', Recovered - ' +str(df.loc[i,'Recovered']) \
                                    +', Death - ' + str(df.loc[i,'Death']) 
                                    
    '''
    
    for var in  [df.columns[i] for i in [2,8,3,4,5]]:
        print('Generating plot for - '+var)
    
        for i in range(0,len(df)):
            df.loc[i,'StateInfo'] = df.loc[i,'State_2'] \
                                    + ', '+var+' :' + str('{:,.0f}'.format(df.loc[i,var]))
        df1 = df[df[var]>0]
        # Initialize the map:
        m = folium.Map(location=[20.5937,78.9629], tiles="OpenStreetMap", zoom_start=4)
            
        if plot_type == 1:
           for i in range(0,len(df1)):
               folium.CircleMarker(
                  location=[df1.iloc[i]['Latitude'], df1.iloc[i]['Longitude']],
                  popup=df.iloc[i]['StateInfo'],
                  radius=float(int(df1.iloc[i][var])),
                  color='crimson',
                  fill=True,
                  fill_color='crimson'
               ).add_to(m)
        elif plot_type == 2:
            # Add the color for the chloropleth:
            m.choropleth(
             geo_data=data,
             name='choropleth',
             data=df1,
             columns=['State_2',var],
             key_on= "feature.properties.NAME_1",
             fill_color='OrRd',
             fill_opacity=0.7,
             line_opacity=0.2,
             legend_name=var,
             highlight = True
            )
            #popup=df.iloc[i]['States'],
            marker_cluster = MarkerCluster().add_to(m)
            for i in range(0,len(df1)):
                folium.Marker(
                          location=[df1.iloc[i]['Latitude'], df1.iloc[i]['Longitude']],
                          popup=df1.iloc[i]['StateInfo']
                       ).add_to(marker_cluster)
            
            folium.LayerControl().add_to(m)
     
        # Save map as html
        m.save(str(data_path)+var+'.html')
        if req_plot==True:
            webbrowser.open_new_tab(str(data_path) +var+'.html')
    

    print('Plot Updated...')
    
    #return(mdt)
   
############
url2 = 'https://www.worldometers.info/coronavirus/#countries'
def WorldDataScrapper(url2=url2,req_plot = False,plot_type = 2):

    page = requests.get(url2)
    #Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    #Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')
    #Check the length of the first 12 rows
    col_len = max([len(T) for T in tr_elements])
    col_list = [len(T) == col_len for T in tr_elements]
    
    new_list = []
    for i in range(0,len(tr_elements)):
        if col_list[i] == True:
            new_list.append(tr_elements[i])
            
    #Check
    if (max([len(T) for T in new_list]) != min([len(T) for T in new_list])):
        print('Table structure has changed. Cannot Proceed..')
        exit
        
    #Create empty list
    col=[]
    i=0
    #For each row, store each first element (header) and an empty list
    for t in new_list[0]:
        i+=1
        name=t.text_content()
        #print '%d:"%s"'%(i,name)
        col.append((name,[]))
    
    br = False
    #Since out first row is the header, data is stored on the second row onwards
    for j in range(1,len(new_list)):
        #T is our j'th row
        T=new_list[j]
        
        #If row is not of size 10, the //tr data is not from our table 
        if len(T)!=col_len:
            exit
        
        #i is the index of our column
        i=0
        
        #Iterate through each element of the row
        for t in T.iterchildren():
            data=t.text_content()
            
            #Stop before total row
            if data =='Total:':
                br = True
                break
            #Check if row is empty
            if i>0:
            #Convert any numerical value to integers
                try:
                    data=int(data)
                except:
                    pass
            #Append the data to the empty list of the i'th column
            col[i][1].append(data)
            #Increment i for the next column
            i+=1
        if br == True:
            break
        #print(j)
    #print(col)
    #close coonection with url
    page.connection.close()
    #[len(C) for (title,C) in col]
    
    Dict={title:column for (title,column) in col}
    df=pd.DataFrame(Dict)
    
    for i in ['TotalCases','TotalDeaths','TotalRecovered','NewCases']:
        s = []
        for st in df[i]:
            #print(st)
            if isinstance(st,int):
                s.append(st)
            elif st =='':
                s.append(0)
            elif st ==' ':
                s.append(0)
            elif st =='  ':
                s.append(0)
            else:
                st = st.strip('+')
                st = int(st.replace(',', ''))
                s.append(st)
        df[i] = s
   
    
    df.ActiveCases = df.TotalCases - (df.TotalDeaths + df.TotalRecovered)
   
    Date = datetime.now().strftime('%Y-%m-%d')
    Time = datetime.now().strftime('%H:%M:%S')
    df = df.assign(Date = Date)
    df = df.assign(Time = Time)
    
    df = df[['Country,Other','TotalCases','ActiveCases','TotalRecovered','TotalDeaths','Date','Time','NewCases']]
    df.columns = ['Country_1','TotalCases','ActiveCases','Recovered','Death','Date','Time','NewCases']
    
    s = []
    for i in df.Country_1:
        #print(i)
        i = i.replace('*', '')
        if i == 'Curaçao':
            i = 'Curacao'
        elif i == 'Réunion': 
            i = 'Reunion'
        s.append(i.strip())
    
    df.Country_1 = s
    
    print('Total Cases: ' + str(sum(df['TotalCases']))+' As of: '+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    mdt= pd.read_csv(str(data_path)+ 'WorldCoronaData.csv')
    #Import Lat Long
    geo_data = pd.read_csv(str(data_path)+ 'CountryLL.csv')
    
    #Import GeoJson file
    state_geo = str(data_path)+ 'world-countries.json'
    with open(state_geo) as f:
        data = json.load(f)
    
    '''
    nm =[]
    for feature in data['features']:
        print(feature['properties']['name'])
        nm.append(feature['properties']['name'])
    '''
    
    if(max(mdt['Date']) == Date):
        sdt = mdt[mdt['Date'] == Date]
        today = True
    else:
        sdt = mdt[mdt['Date'] == max(mdt['Date'])]
        sdt = sdt.assign(NewCases = 0)
        today = False

    NewCase = []
    CaseSince = []
    Geo = []
    for i in df['Country_1']:
        #NewCase
        
        if len(sdt.loc[sdt['Country_1'] == i,]) == 0 :
            continue
        
        TC_N = int(df.loc[df['Country_1'] == i,'TotalCases']) 
        TC_O = int(sdt.loc[sdt['Country_1'] == i,'TotalCases'])
        NC = TC_N - TC_O   
        NC_O = int(sdt.loc[sdt['Country_1'] == i,'NewCases'])
        NewCase.append(NC_O + NC)
        
        #No new case since
        NNC_O = int(sdt.loc[sdt['Country_1'] == i,'NoNewCasesSince'])
        if today == False:
            NNC = 0 if NC > 0 else NNC_O + 1
        else:
            NNC = 0 if NC > 0 else NNC_O
        
        CaseSince.append(NNC)
        Geo.append(i)
    
    
    new = pd.DataFrame({'Country_1': Geo,
                       #'NewCases' : NewCase,
                       'NoNewCasesSince' : CaseSince
                       })
    
    df = pd.merge(df, new, on='Country_1', how='left')
    df = df.replace(np.nan,0)
    
    print('New cases for today - ',str(sum(df['NewCases'])))
    
    if today == True:
        mdt = mdt.loc[-(mdt['Date']==Date),]        
        mdt = mdt.append(df)
    else:
        mdt = mdt.append(df)
        
    #Write csv
    mdt.to_csv (str(data_path)+ 'WorldCoronaData.csv', index = None, header=True)
    print('Data Updated...')
    
    df = pd.merge(df, geo_data, on='Country_1', how='left')
    
       # i = 1
       # var = df.columns[i]
    for var in  [df.columns[i] for i in [1,7,2,3,4]]:
        print('Generating plot for - '+var)
    
        for i in range(0,len(df)):
            df.loc[i,'StateInfo'] = df.loc[i,'Country_1'] \
                                    + ', '+var+' :' + str('{:,.0f}'.format(df.loc[i,var])) 
        df1 = df[df[var]>0]
        df1 = df1.dropna()
        # Initialize the map:
        m = folium.Map(location=[20, 0], tiles="OpenStreetMap", zoom_start=1)
            
        
        if plot_type == 1:
           
            for i in range(0,len(df1)):
               folium.CircleMarker(
                  location=[df1.iloc[i]['Latitude'], df1.iloc[i]['Longitude']],
                  popup=df.iloc[i]['StateInfo'],
                  radius=float(int(df1.iloc[i][var])/1000),
                  color='crimson',
                  fill=True,
                  fill_color='crimson'
                  ).add_to(m)
               
        elif plot_type == 2:
            
            # Add the color for the chloropleth:
            m.choropleth(
             geo_data=data,
             name='choropleth',
             data=df1,
             columns=['Country_2',var],
             key_on= "feature.properties.name",
             fill_color='OrRd',
             fill_opacity=0.7,
             line_opacity=0.2,
             legend_name=var,
             highlight = True
            )
            
            
            marker_cluster = MarkerCluster().add_to(m)
            for i in range(0,len(df1)):
                folium.Marker(
                          location=[df1.iloc[i]['Latitude'], df1.iloc[i]['Longitude']],
                          popup=df1.iloc[i]['StateInfo']
                       ).add_to(marker_cluster)
            
            folium.LayerControl().add_to(m)

     
        # Save map as html
        m.save(str(data_path)+ 'World_' +var+'.html')
        if req_plot==True:
            webbrowser.open_new_tab(str(data_path)+ 'World_' +var+'.html')
    

    print('Plot Updated...')
    #return(mdt)

def call_functions():
    print('Updating World Data..')
    WorldDataScrapper()
    print('Updating India Data..')
    DataScrapper()    

UPDADE_INTERVAL = 60*10

def get_new_data_every(period=UPDADE_INTERVAL):
    """Update the data every 'period' seconds"""
    while True:
        call_functions()    
        print('system sleeping for {} seconds'.format(UPDADE_INTERVAL))
        time.sleep(period)
        
        #global data

get_new_data_every()
'''
def start_multi():
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(call_functions)
    
    
if __name__ == '__main__':
    start_multi()
    call_functions()
 '''   
########### Test

#import copy
#mdt= copy.deepcopy(dt)



'''
value = mdt.State_1.unique()[0]
dt = pd.DataFrame(sorted(mdt.Date.unique()),columns = ['Date'])
    dff = mdt.loc[mdt.State_1 == value,['Date','State_1','TotalCases','NewCases','ActiveCases','Recovered','Death']]
    dff = pd.merge(dt, dff, on='Date', how='left')
    dff = dff.replace(np.nan,0)

    dff = mdt.loc[,['Date','State_1','TotalCases','NewCases','ActiveCases','Recovered','Death']]
    dff = mdt.groupby(['Date']).agg({  'TotalCases' :sum,
                                       'NewCases': sum,
                                       'ActiveCases': sum,
                                       'Recovered':sum,
                                       'Death':sum
                                   })
    dff = dff.replace(np.nan,0)
    
    dff = pd.merge(dt, dff, on='Date', how='left')
    dff = dff.replace(np.nan,0)


'''

    
