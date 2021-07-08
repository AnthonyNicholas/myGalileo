"""
Process-sleep-data.py
Processes fitbit sleep data files, uploads data into fitbit dataframe, outputs graphs.
"""  	

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  
import streamlit as st
try:
    import plotly.express as px
    import plotly.graph_objects as go 
    PLOTLY = True
except:
    PLOTLY = False
    raise(Exception('need to install plotly'))
from tqdm.auto import tqdm
import seaborn as sns    

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import SimpleImputer#, IterativeImputer
import copy

import time
import numpy as np
import os
if 'DYNO' in os.environ:
    heroku = True
else:
    heroku = False

# Function: process_fitbit_sleep_data()
# fileList: A list of fitbit sleep data files eg ["sleep-2020-03-09.json","sleep-2020-04-08.json".....]
# Returns a dataframe with the following columns:
# ['duration', 'efficiency', 'endTime', 'mainSleep', 'minutesAfterWakeup', 'minutesAsleep', 'minutesAwake', 'minutesToFallAsleep', 'startTime', 'summary.asleep.count', 'summary.asleep.minutes', 'summary.awake.count', 'summary.awake.minutes', 'summary.deep.count', 'summary.deep.minutes', 'summary.deep.thirtyDayAvgMinutes', 'summary.light.count', 'summary.light.minutes', 'summary.light.thirtyDayAvgMinutes', 'summary.rem.count', 'summary.rem.minutes', 'summary.rem.thirtyDayAvgMinutes', 'summary.restless.count', 'summary.restless.minutes', 'summary.wake.count', 'summary.wake.minutes', 'summary.wake.thirtyDayAvgMinutes', 'timeInBed', 'type', 'dayOfWeek', 'rem.%', 'deep.%', 'wake.%', 'light.%', 'startMin', 'endMin']

sns_colorscale = [[0.0, '#3f7f93'], #cmap = sns.diverging_palette(220, 10, as_cmap = True)
[0.071, '#5890a1'],
[0.143, '#72a1b0'],
[0.214, '#8cb3bf'],
[0.286, '#a7c5cf'],
[0.357, '#c0d6dd'],
[0.429, '#dae8ec'],
[0.5, '#f2f2f2'],
[0.571, '#f7d7d9'],
[0.643, '#f2bcc0'],
[0.714, '#eda3a9'],
[0.786, '#e8888f'],
[0.857, '#e36e76'],
[0.929, '#de535e'],
[1.0, '#d93a46']]


def cluster_map_corr(df):
    #st.write('this method mutated df columns, has side effects watch out')
    
    if 'endTime' in df.columns:
        del df['endTime']
        del df['dayOfWeek']
        del df['startTime']
        del df['type']
        del df['mainSleep']

    #
    
    g = sns.clustermap(df.corr())
    plt.title('Cluster map of correlation matrix')#+str(title))#, fontsize=14)
    st.pyplot()
    reduced_df = df
    return reduced_df


def cluster_map_cov(df):
    g = sns.clustermap(df.cov())
    plt.title('Cluster map of covariance matrix')#+str(title))#, fontsize=14)
    st.pyplot()
    return df
def covariance_matrix(df):
    # Covariance

    colormap = plt.cm.RdBu
    sns.set(style='whitegrid')#, rc={"grid.linewidth": 0.1})
    #sns.set_context("paper", font_scale=1.9)   
    svm = sns.heatmap(df.cov(),
                square=True,linecolor='white')    
    cols = ['duration', 'efficiency', 'summary.deep.minutes', 'summary.deep.minutes.%', 'summary.light.minutes', 'summary.light.minutes.%', 'summary.rem.minutes', 'summary.rem.minutes.%', 'summary.wake.minutes', 'summary.wake.minutes.%', 'startMin', 'avg4_startMin', 'startTimeDeviation1.%', 'startTimeDeviation4.%']
    plt.xticks(range(df.shape[1]), cols, rotation="vertical")
    plt.yticks(range(df.shape[1]), cols)

    plt.title('Covariance Matrix', fontsize=14)
    st.pyplot()

#@st.cache
'''
depricated
def df_derived_by_shift(df,lag=0,NON_DER=[]):
    # https://www.kaggle.com/dedecu/cross-correlation-time-lag-with-pandas
    df = df.copy()
    if not lag:
        return df
    cols ={}
    for i in range(1,lag+1):
        for x in list(df.columns):
            if x not in NON_DER:
                if not x in cols:
                    cols[x] = ['{}_{}'.format(x, i)]
                else:
                    cols[x].append('{}_{}'.format(x, i))
    for k,v in cols.items():
        columns = v
        dfn = pd.DataFrame(data=None, columns=columns, index=df.index)    
        i = 1
        for c in columns:
            dfn[c] = df[k].shift(periods=i)
            i+=1
        df = pd.concat([df, dfn], axis=1, join_axes=[df.index])
    return df
'''


def try_to_impute(temp_df):
    # Drop categorical columns as the imputer can't handle strings

    temp_df = temp_df.apply(pd.to_numeric, errors='coerce')
    temp_df.dropna(axis=0, how='any',inplace=True, thresh=5)
    temp_df.reset_index(drop=True)
    '''
    imp = IterativeImputer(random_state=0)
    X = temp_df.values[:]
    imp.fit(X)
    temp_df.values[:] = imp.transform(X)
    '''

    return temp_df

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

def animated_deep_sleep(sleep_df, cols):
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    last_rows = (0,0)#np.random.randn(1, 1)
    chart = st.line_chart(last_rows)
    X = [i for i in range(0,len(sleep_df.index.values))]
    cnt = 0 
    for i in sleep_df.index:
        #new_rows_rem = pd.Series(sleep_df.loc[i,'rem.%'])
        new_rows_deep = pd.Series(sleep_df.loc[i,'deep.%'])
        try:
            #chart.add_rows(new_rows_rem)
            chart.add_rows(new_rows_deep)
            status_text.text("%i%% Complete" % cnt)
            
            progress_bar.progress(X[cnt])
            cnt+=1
        except:
            pass
        time.sleep(0.01)
    progress_bar.empty()

    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
    #st.button("Re-run") 
    return None 

def animated_rem_sleep(sleep_df, cols):
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    last_rows = (0,0)#np.random.randn(1, 1)
    chart = st.line_chart(last_rows)
    X = [i for i in range(0,len(sleep_df.index.values))]
    cnt = 0 
    for i in sleep_df.index:
        new_rows_rem = pd.Series(sleep_df.loc[i,'rem.%'])
        #new_rows_deep = pd.Series(sleep_df.loc[i,'rem.%'])
        try:
            chart.add_rows(new_rows_rem)
            status_text.text("%i%% Complete" % cnt)
            cnt+=1
            progress_bar.progress(X[cnt])
        except:
            pass
        time.sleep(0.01)
    progress_bar.empty()

    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
    #st.button("Re-run")    
    return None
def plot_sleep_data_joint(full_sleep_df, col1, col2):
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=0.5)   

    fig = sns.jointplot(x=full_sleep_df[col1], y=full_sleep_df[col2],kind='hex')

    plt.ylabel(col2)
    plt.xlabel(col1)
    st.pyplot()

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


# Function: plot_sleep_data_scatter_plotly(sleep_df)
# Function plots a scatter plot for two coloumns of the dataframe.
# sleep_df: pandas DataFrame
def plot_sleep_data_scatter_plotly(full_sleep_df, col1, col2):
    fig = px.scatter(x=full_sleep_df[col1], y=full_sleep_df[col2],labels={
                     "x": col1,
                     "y": col2                 
                },
                title="Sleep plot")

    st.write(fig)

COLS = ['duration', 'efficiency', 
'summary.deep.minutes', 'summary.deep.minutes.%', 
'summary.light.minutes', 'summary.light.minutes.%', 
'summary.rem.minutes', 'summary.rem.minutes.%', 
'summary.wake.minutes', 'summary.wake.minutes.%',
    'startMin', 'avg4_startMin', 
    'startTimeDeviation1.%', 'startTimeDeviation4.%']
# Function: plot_corr(sleep_df)
# Function plots a graphical correlation matrix for each pair of columns in the dataframe.
# sleep_df: pandas DataFrame

def plot_corr(sleep_df,title=None):

    f = plt.figure(figsize=(19, 15))

    colormap = plt.cm.RdBu
    plt.figure(figsize=(15,10))
    plt.title(u'no lag yet', y=1.05, size=16)
    mask = np.zeros_like(sleep_df.corr())
    mask[np.triu_indices_from(mask)] = True
    fig = sns.heatmap(sleep_df.corr(),mask=mask,
        linewidths=0.1,square=True, linecolor='white')
 
    plt.xticks(range(sleep_df.shape[1]), COLS, fontsize=12, rotation="vertical")
    plt.yticks(range(sleep_df.shape[1]), COLS, fontsize=12)
    if title is not None:
        plt.title('Correlation Matrix'+str(title))#, fontsize=14)
    else:
        plt.title('Correlation Matrix')#+str(title))#, fontsize=14)

    st.pyplot()

def df_to_plotly(df,log=False):
    return {'z': df.values.tolist(),
            'x': df.columns.tolist(),
            'y': df.index.tolist()}


def plot_df_plotly(sleep_df):
    fig = go.Figure(data=go.Heatmap(df_to_plotly(sleep_df,log=True)))
    st.write(fig)

def plot_imshow_plotly(sleep_df):

    heat = go.Heatmap(df_to_plotly(sleep_df),colorscale=sns_colorscale)
    #fig = go.Figure(data=

    title = 'Correlation Matrix'               

    layout = go.Layout(title_text=title, title_x=0.5, 
                    width=600, height=600,
                    xaxis_showgrid=False,
                    yaxis_showgrid=False,
                    yaxis_autorange='reversed')
    
    fig=go.Figure(data=[heat], layout=layout)      

    st.write(fig)


def crosscorr(datax, datay, lag=0, wrap=False):
    """ Lag-N cross correlation. 
    Shifted data filled with NaNs 
    Next :
    https://stackoverflow.com/questions/33171413/cross-correlation-time-lag-correlation-with-pandas
    Parameters
    ----------
    lag : int, default 0
    datax, datay : pandas.Series objects of equal length
    Returns
    ----------
    crosscorr : float
    """
    if wrap:
        shiftedy = datay.shift(lag)
        shiftedy.iloc[:lag] = datay.iloc[-lag:].values
        return datax.corr(shiftedy)
    else: 
        return datax.corr(datay.shift(lag))
def check_time_lags(df,col0,col1):
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=3.9)                                                  
    #plt.figure(figsize=(3.1, 3)) # Two column paper. Each column is about 3.15 inch wide.                                                                                                                                                                                                                                 
    #color = sns.color_palette("Set2", 6)
    # https://towardsdatascience.com/granger-causality-and-vector-auto-regressive-model-for-time-series-forecasting-3226a64889a6
    d1 = df[col0]
    d2 = df[col1]
    hours = 5
    days = 30
    #https://gist.github.com/jcheong0428/7d5759f78145fc0dc979337f82c6ea33
    #seconds = 5
    #fps = 30
    rs = [crosscorr(d1,d2, lag) for lag in range(-int(hours*days),int(hours*days+1))]
    offset = np.ceil(len(rs)/2)-np.argmax(rs)
    f,ax=plt.subplots(figsize=(20,13))
    re_title = 'look for time lags when correlation is \n \
                 maximised (peak synchrony) betwen {0} and {1}'.format(col0,col1)
    ax.plot(rs)
    ax.axvline(np.ceil(len(rs)/2),color='k',linestyle='--',label='Center',linewidth=11.0)
    ax.axvline(np.argmax(rs),color='r',linestyle='--',label='Peak synchrony',linewidth=11.0)
    ax.set(title=f'Offset = {offset} frames\nS1 leads <> S2 leads'+re_title,ylim=[.1,.31],xlim=[0,301], xlabel='Offset',ylabel='Pearson r')
    ax.set_xticks([0, 50, 100, 151, 201, 251, 301])
    ax.set_xticklabels([-150, -100, -50, 0, 50, 100, 150]);
    plt.legend()  
    st.pyplot()


