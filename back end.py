# essential libraries
#import math
#import random
#from datetime import timedelta
#from urllib.request import urlopen
#import json
# storing and anaysis
import numpy as np
import pandas as pd

# visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
# import calmap
#import folium

# color pallette
cnf, dth, rec, act = '#393e46', '#ff2e63', '#21bf73', '#fe9801' 

# converter
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()   

# hide warnings
#import warnings
#warnings.filterwarnings('ignore')


class Covid19:
    full_table = None
    def __init__(self,state_name,case):
        self.full_grouped = None
        self.day_wise = None
        self.state_wise = None
        self.state_name = state_name
        self.case = case
        pass
    def Get_value(self):
        self.full_table = pd.read_csv('complete.csv')
        self.full_table = self.full_table[['Date', 'Name of State / UT', 'Total Confirmed cases', 'Death', 'Cured/Discharged/Migrated', 'Latitude',
             'Longitude']]
        self.full_table.columns = ['Date', 'State/UT', 'Confirmed', 'Deaths', 'Recovered', 'Lat', 'Long']
    def Preprocessing(self):
        # Add total active case in dataframe
        self.full_table['Active'] = self.full_table['Confirmed'] - self.full_table['Deaths'] - self.full_table['Recovered']
        # fixing datatypes
        self.full_table['Recovered'] = self.full_table['Recovered'].astype(int)
        # Grouped by day, State/UT
        # =======================

        self.full_grouped = self.full_table.groupby(['Date', 'State/UT'])[
            'Confirmed', 'Deaths', 'Recovered', 'Active'].sum().reset_index()

        # new cases ======================================================
        temp = self.full_grouped.groupby(['State/UT', 'Date', ])['Confirmed', 'Deaths', 'Recovered']
        temp = temp.sum().diff().reset_index()

        mask = temp['State/UT'] != temp['State/UT'].shift(1)

        temp.loc[mask, 'Confirmed'] = np.nan
        temp.loc[mask, 'Deaths'] = np.nan
        temp.loc[mask, 'Recovered'] = np.nan

        # renaming columns
        temp.columns = ['State/UT', 'Date', 'New cases', 'New deaths', 'New recovered']
        # =================================================================

        # merging new values
        self.full_grouped = pd.merge(self.full_grouped, temp, on=['State/UT', 'Date'])

        # filling na with 0
        self.full_grouped = self.full_grouped.fillna(0)

        # fixing data types
        cols = ['New cases', 'New deaths', 'New recovered']
        self.full_grouped[cols] = self.full_grouped[cols].astype('int')

        self.full_grouped['New cases'] = self.full_grouped['New cases'].apply(lambda x: 0 if x < 0 else x)

    def Day_wise(self):
        # Day wise
        # ========

        # table
        self.day_wise = self.full_grouped.groupby('Date')[
            'Confirmed', 'Deaths', 'Recovered', 'Active', 'New cases', 'New deaths'].sum().reset_index()

        # number cases per 100 cases
        self.day_wise['Deaths / Cases'] = round((self.day_wise['Deaths'] / self.day_wise['Confirmed']), 2)
        self.day_wise['Recovered / Cases'] = round((self.day_wise['Recovered'] / self.day_wise['Confirmed']), 2)
        self.day_wise['Deaths / Recovered'] = round((self.day_wise['Deaths'] / self.day_wise['Recovered']), 2)

        # no. of countries
        self.day_wise['No. of State/UT'] = self.full_grouped[self.full_grouped['Confirmed'] != 0].groupby('Date')[
            'State/UT'].unique().apply(len).values

        # fillna by 0
        cols = ['Deaths / Cases', 'Recovered / Cases', 'Deaths / Recovered']
        self.day_wise[cols] = self.day_wise[cols].fillna(0)
    def State_wise(self):
        # Country wise
        # ============

        # getting latest values
        self.state_wise = self.full_grouped[self.full_grouped['Date'] == max(self.full_grouped['Date'])].reset_index(drop=True).drop('Date',
                                                                                                                 axis=1)

        # group by country
        self.state_wise = self.state_wise.groupby('State/UT')[
            'Confirmed', 'Deaths', 'Recovered', 'Active', 'New cases'].sum().reset_index()

        # per 100 cases
        self.state_wise['Deaths / Cases'] = round((self.state_wise['Deaths'] / self.state_wise['Confirmed']), 2)
        self.state_wise['Recovered / Cases'] = round((self.state_wise['Recovered'] / self.state_wise['Confirmed']), 2)
        self.state_wise['Deaths / Recovered'] = round((self.state_wise['Deaths'] / self.state_wise['Recovered']), 2)

        cols = ['Deaths / Cases', 'Recovered / Cases', 'Deaths / Recovered']
        self.state_wise[cols] = self.state_wise[cols].fillna(0)

    def Confirmed_case(self):
        self.full_table = self.full_table[self.full_table['State/UT'].str.contains(self.state_name)]
        temp = self.full_table.groupby('Date')[self.case].sum().reset_index()
        temp = temp.melt(id_vars="Date", value_vars=self.case,
                         var_name='Case', value_name='Count')
        temp.head()
        if self.case =='Active':
            fig = px.area(temp, x="Date", y="Count", color='Case', height=600,
                          title='{} Ative Case'.format(self.state_name), color_discrete_sequence=[act])
        elif self.case =='Deaths':
            fig = px.area(temp, x="Date", y="Count", color='Case', height=600,
                          title='{} Deaths Case'.format(self.state_name), color_discrete_sequence=[dth])
        elif self.case =='Confirmed':
            fig = px.area(temp, x="Date", y="Count", color='Case', height=600,
                          title='{} Confirmed Case'.format(self.state_name), color_discrete_sequence=[cnf])
        elif self.case =='Recovered':
            fig = px.area(temp, x="Date", y="Count", color='Case', height=600,
                          title='{} Recovered Case'.format(self.state_name), color_discrete_sequence=[rec])
        else:
            print("Please Enter correct value !")
            exit()
        fig.update_layout(xaxis_rangeslider_visible=True)
        fig.write_html("jk.html")
    def Execution(self):
        self.Get_value()
        self.Preprocessing()
        self.Day_wise()
        self.State_wise()
        self.Confirmed_case()

if __name__ == "__main__":
    state_name = ("Bihar")
    case = ("Active")
    covid = Covid19(state_name,case)
    covid.Execution()