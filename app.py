"""
Process-sleep-data.py
Processes fitbit sleep data files, uploads data into fitbit dataframe, outputs graphs.
"""  	

import pandas as pd
import numpy as np
import datetime as dt  
import matplotlib.pyplot as plt  
from datetime import datetime                          
import streamlit as st
try: 
    json_normalize = pd.json_normalize
except:
    from pandas.io.json import json_normalize

try:
    import plotly.express as px
    import plotly.graph_objects as go # or plotly.express as px

    PLOTLY = True
except:
    PLOTLY = False

import cufflinks as cf
import seaborn as sns    
# Function: process_fitbit_sleep_data()
# fileList: A list of fitbit sleep data files eg ["sleep-2020-03-09.json","sleep-2020-04-08.json".....]
# Returns a dataframe with the following columns:
# ['duration', 'efficiency', 'endTime', 'mainSleep', 'minutesAfterWakeup', 'minutesAsleep', 'minutesAwake', 'minutesToFallAsleep', 'startTime', 'summary.asleep.count', 'summary.asleep.minutes', 'summary.awake.count', 'summary.awake.minutes', 'summary.deep.count', 'summary.deep.minutes', 'summary.deep.thirtyDayAvgMinutes', 'summary.light.count', 'summary.light.minutes', 'summary.light.thirtyDayAvgMinutes', 'summary.rem.count', 'summary.rem.minutes', 'summary.rem.thirtyDayAvgMinutes', 'summary.restless.count', 'summary.restless.minutes', 'summary.wake.count', 'summary.wake.minutes', 'summary.wake.thirtyDayAvgMinutes', 'timeInBed', 'type', 'dayOfWeek', 'rem.%', 'deep.%', 'wake.%', 'light.%', 'startMin', 'endMin']


from tqdm.auto import tqdm
import streamlit as st


class tqdm:
    def __init__(self, iterable, title=None):
        if title:
            st.write(title)
        self.prog_bar = st.progress(0)
        self.iterable = iterable
        self.length = len(iterable)
        self.i = 0

    def __iter__(self):
        for obj in self.iterable:
            yield obj
            self.i += 1
            current_prog = self.i / self.length
            self.prog_bar.progress(current_prog)
def process_fitbit_sleep_data(fileList):
    full_sleep_df = None
    for input_file in tqdm(fileList,title='Loading in fitbit data'):
        input_df = pd.read_json(input_file)
        detail_df = json_normalize(input_df['levels'])
        sleep_df = pd.concat([input_df, detail_df], axis =1)
        full_sleep_df = pd.concat([full_sleep_df, sleep_df], sort=True)

    full_sleep_df['dateOfSleep']= pd.to_datetime(full_sleep_df['dateOfSleep'])
    full_sleep_df['dayOfWeek'] = full_sleep_df['dateOfSleep'].dt.day_name()
    full_sleep_df = full_sleep_df.set_index('dateOfSleep')
    full_sleep_df.sort_index(inplace=True)

    full_sleep_df['duration'] = full_sleep_df['duration']/(1000*60) # convert duration to minutes

    for col in ['rem','deep','wake','light']:
        full_sleep_df[col + '.%'] = 100*full_sleep_df['summary.' + col + '.minutes']/full_sleep_df['duration']

    full_sleep_df['startMin'] = pd.to_datetime(full_sleep_df['startTime']).dt.minute + 60 * pd.to_datetime(full_sleep_df['startTime']).dt.hour

    full_sleep_df['startMin'] = np.where(full_sleep_df['startMin'] < 240, full_sleep_df['startMin'] + 1440, full_sleep_df['startMin']) # handle v late nights

    full_sleep_df['endMin'] = pd.to_datetime(full_sleep_df['endTime']).dt.minute + 60 * pd.to_datetime(full_sleep_df['endTime']).dt.hour

    #remove rows which are not mainSleep == True (these are naps not sleeps)
    full_sleep_df = full_sleep_df[full_sleep_df.mainSleep != False]

    #remove column which are not needed/useful
    full_sleep_df.drop(['logId', 'data', 'shortData', 'infoCode', 'levels'], axis=1, inplace=True)

    return full_sleep_df

# Function: plot_fitbit_sleep_data()
# sleep_df: a sleep dataframe
# cols: the columns to be displayed on the line graph
# output: saves a line graph to a png file named according to the columns graphed (with vertical lines to indicate weekends)
def plot_fitbit_sleep_data(sleep_df, cols):
    sleep_df[cols].plot(figsize=(20,5))
    plt.title('Sleep plot')

    for date in sleep_df.index[sleep_df['dayOfWeek'] == 'Monday'].tolist():
        plt.axvline(date)

    output_filename = "sleep"
    for col in cols:
        output_filename += "-" + col
    
    output_filename += ".png"
    #plt.savefig(output_filename, dpi=100)
    #plt.close()	
    st.pyplot()
def plot_fitbit_sleep_data_plotly(sleep_df, cols):

    X = [i for i in range(0,len(sleep_df.index.values))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=X, y=sleep_df['rem.%'],
                        mode='lines',
                        name='REM sleep'))
    fig.add_trace(go.Scatter(x=X, y=sleep_df['deep.%'],
                        mode='lines+markers',
                        name='deep sleep'))
    st.write(fig)

# Function: plot_sleep_data_scatter 
# sleep_df: a sleep dataframe
# cols: the columns to be displayed on the scatter plot
# output: saves a scatter plot to a png file named according to the columns graphed
def plot_sleep_data_scatter(full_sleep_df, col1, col2):
    full_sleep_df.plot.scatter(x=col1, y=col2)
    plt.title('Sleep plot')
    plt.ylabel(col2)
    plt.xlabel(col1)
    st.pyplot()

def plot_sleep_data_scatter_plotly(full_sleep_df, col1, col2):
    fig = px.scatter(x=full_sleep_df[col1], y=full_sleep_df[col2])
    st.write(fig)
    #output_filename = "sleep-scatter-" + col1 + "-" + col2 + ".png"
    #plt.savefig(output_filename, dpi=100)
    #plt.close()	

# Function: plot_corr(sleep_df)
# Function plots a graphical correlation matrix for each pair of columns in the dataframe.
# sleep_df: pandas DataFrame

def plot_corr(sleep_df):

    f = plt.figure(figsize=(19, 15))
    #plt.matshow(sleep_df.corr(), fignum=f.number)
    fig = sns.heatmap(sleep_df.corr())#,annot=True)
    
    cols = ['duration', 'efficiency', 'summary.deep.minutes', 'summary.deep.minutes.%', 'summary.light.minutes', 'summary.light.minutes.%', 'summary.rem.minutes', 'summary.rem.minutes.%', 'summary.wake.minutes', 'summary.wake.minutes.%', 'startMin', 'avg4_startMin', 'startTimeDeviation1.%', 'startTimeDeviation4.%']
    plt.xticks(range(sleep_df.shape[1]), cols, fontsize=12, rotation="vertical")
    plt.yticks(range(sleep_df.shape[1]), cols, fontsize=12)
    #cb = plt.colorbar()
    #cb.ax.tick_params(labelsize=12)
    plt.title('Correlation Matrix', fontsize=14)

    #st.write(
    st.pyplot()
    #st.pyplot()
def df_to_plotly(df):
    return {'z': df.values.tolist(),
            'x': df.columns.tolist(),
            'y': df.index.tolist()}
def plot_corr_plotly(sleep_df):
 
    fig = go.Figure(data=go.Heatmap(df_to_plotly(sleep_df)))

    st.write(fig)
    
#if __name__ == "__main__":  
st.title('Inner Galileo Fitbit analysis for sleep and Major Depressive Disorder')

fileList = ["sleep-2020-03-09.json","sleep-2020-04-08.json","sleep-2020-05-08.json","sleep-2020-06-07.json","sleep-2020-07-07.json"]
st.markdown('''
This is a markdown string that explains sleep data from date {0}
'''.format(str('2020-03-09')))


sleep_df = process_fitbit_sleep_data(fileList)
st.write(sleep_df, unsafe_allow_html=True)

plot_fitbit_sleep_data_plotly(sleep_df, ['rem.%', 'deep.%'])

#plot_fitbit_sleep_data(sleep_df, ['rem.%', 'deep.%'])
#if PLOTLY:
plot_sleep_data_scatter_plotly(sleep_df, 'startMin', 'deep.%')
#else:
#plot_sleep_data_scatter(sleep_df, 'startMin', 'deep.%')
#if PLOTLY:


#else:
plot_corr(sleep_df)
#leep_df = process_fitbit_sleep_data(fileList)
'''
Next :
https://stackoverflow.com/questions/33171413/cross-correlation-time-lag-correlation-with-pandas
'''
plot_corr_plotly(sleep_df)

st.markdown('done')