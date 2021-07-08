"""
Process-sleep-data.py
Processes fitbit sleep data files, uploads data into fitbit dataframe, outputs graphs.
"""  	

import pandas as pd
import numpy as np                       
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go # or plotly.express as px
DEBUG_WITHOUT_PLOTLY = False
import sklearn   
import plotting_functions as pf
from utils import process_fitbit_sleep_data, process_fitbit_other_data, visit_files
import utils 
CACHED = True
BIG_DATA = True
import os
import glob
import requests
# sense if running on heroku
if 'DYNO' in os.environ:
    heroku = False
else:
    heroku = True

if __name__ == "__main__":  
    st.title('The Quantified Sleep')

    API_TOKEN = st.text_input('Please Enter Your Fitbit API token:')
    st.text("API TOKEN is", API_TOKEN)
    URL = "https://api.fitbit.com/1.2/user/~/sleep/date/2020-08-18.json"
    responses = requests.request("GET",url,data=payload,headers=headers)
    radio_value = st.sidebar.radio("\
		Are you more interested in Sleep/Exercise/the interplay between them"
		,["Sleep","Exercise","Interplay"])
    # radio_value = st.sidebar.radio("Target Number of Samples",[10,20,30])

    if CACHED:

        fileList = ["sleep-2020-03-09.json","sleep-2020-04-08.json","sleep-2020-05-08.json","sleep-2020-06-07.json","sleep-2020-07-07.json"]
        fileList=[ str("original_data/")+str(f) for f in fileList]
        st.markdown('Analysis for sleep quality')

        st.markdown('''We are mining and exploring sleep data fro
        m date {0}
        '''.format(str('2020-03-09')))
    else:
        print('add methods for user upload data')
        

    if not DEBUG_WITHOUT_PLOTLY:
        if BIG_DATA:
            files = glob.glob('data/*.json')
            list_of_lists = visit_files(files)
            big_feature = process_fitbit_other_data(list_of_lists)
            st.text(big_feature.keys())
        #st.markdown('''
        ## Using cached data for splash screen
        #Data cleaning follows
        #'''.format(np.sum(sleep_df.isnull().sum().values)))
        #st.markdown('''---''')

        #pf.plot_df_plotly(sleep_df)#,'rem.%','deep.%')
        sleep_df = utils.process_fitbit_sleep_data(fileList)

        sleep_df.dropna(axis=1, how='any',inplace=True, thresh=4)
        sleep_df = pf.try_to_impute(sleep_df)       
        sleep_df.dropna(axis=1, how='any',inplace=True, thresh=0)
        sleep_df.dropna(axis=0, how='any',inplace=True, thresh=10)
        sleep_df = sleep_df.apply(lambda x: x.fillna(sleep_df.mean()),axis=1)
        #sleep_df.dropna(axis=0,inplace=True)
        st.markdown('''---''')
        st.markdown('''\n\n''')

        '''
        clustergram useful for exploration
        '''
        sleep_df.dropna(axis=0, how='any',inplace=True, thresh=4)
        reduced_df = pf.cluster_map_corr(sleep_df)
        reduced_df.values[:] = sklearn.preprocessing.normalize(reduced_df.values[:])
        '''
        Fully imputed data frame:
        '''
        st.markdown('''---''')
        st.markdown('''\n\n''')

        #pf.animated_deep_sleep(reduced_df, ['rem.%', 'deep.%'])
        #pf.animated_rem_sleep(reduced_df, ['rem.%', 'deep.%'])
        pf.plot_df_plotly(reduced_df)#,'rem.%','deep.%')
        #sleep_df = reduced_df 
        st.markdown('''---''')
        st.markdown('''\n\n''')
        st.write(sleep_df.describe())
        #st.write(reduced_df.describe())

        st.markdown('''Total Nans: {}'''.format(np.sum(sleep_df.isnull().sum().values)))

        st.markdown('''\n\n''')

        pf.plot_fitbit_sleep_data_plotly(sleep_df, ['rem.%', 'deep.%'])
        st.markdown('''---''')
        st.markdown('''\n\n''')

        pf.plot_sleep_data_scatter_plotly(sleep_df, 'startMin', 'deep.%')
        st.markdown('''---''')

        '''
        # hexbins, 
        joint plot show density of data better:
        '''
        pf.plot_sleep_data_joint(sleep_df, 'startMin', 'deep.%')
    
        '''
        If imputation worked there would be no nans visible below:
        need to drop nans
        fill with zero,
        impute zeros with mean
        '''
        st.markdown('''---''')


        pf.plot_corr(sleep_df)
        ''' 
        This is plotly correlation matrix this can be combined with
        seaborn approach and masking
        '''
        st.markdown('''---''')
        reduced_df = pf.cluster_map_cov(sleep_df)

        pf.plot_imshow_plotly(sleep_df.corr())
        '''
        Covariance matrix backbone of PCA, more useful when we have more features
        variables that vary together includes negatively correlations, or non-proporttional changes
        big changes that correlate with small changes (sometimes negatively correlations)

        '''
        st.markdown('''---''')

        pf.covariance_matrix(sleep_df)
        st.markdown('''---''')
        pf.plot_imshow_plotly(sleep_df.cov())
        st.markdown('''---''')
        pf.check_time_lags(sleep_df, 'rem.%', 'deep.%')
        st.markdown('''---''')
        pf.check_time_lags(sleep_df, 'startMin', 'deep.%')




    if DEBUG_WITHOUT_PLOTLY:
        pf.plot_corr(sleep_df)
        pf.plot_fitbit_sleep_data(sleep_df, ['rem.%', 'deep.%'])
        pf.plot_sleep_data_scatter(sleep_df, 'startMin', 'deep.%')



#NFFT=256, Fs=2, Fc=0, detrend=, window=, noverlap=0, pad_to=None, sides=’default’, scale_by_freq=None, *, data=None, **kwargs)
