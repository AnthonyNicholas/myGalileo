
import pandas as pd
import numpy as np  
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt  
#import matplotlib.pyplot as plt  
from datetime import datetime                          
import streamlit as st
try: 
    json_normalize = pd.json_normalize
except:
    from pandas.io.json import json_normalize

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

from tqdm.auto import tqdm

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

#@st.cache(allow_output_mutation=True)            
def process_fitbit_sleep_data(fileList):
    full_sleep_df = None
    cnt = 0
    #tqdm(follow_links,title='Scrape in Progress. Please Wait.')
    for input_file in tqdm(fileList,title='Loading in short interval of sleep fitbit data'):
        input_df = pd.read_json(input_file)
        detail_df = json_normalize(input_df['levels'])
        sleep_df = pd.concat([input_df, detail_df], axis =1)
        full_sleep_df = pd.concat([full_sleep_df, sleep_df], sort=True)
        cnt+=1
        progress_bar.progress(cnt/len(fileList))
        status_text.text("Data Reading {0} Complete".format(100*float(cnt/len(fileList))))    
        

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
'''
import dask
def dask_map_function(eval_,invalid_ind):
    results = []
    for x in invalid_ind:
        y = dask.delayed(eval_)(x)
        results.append(y)
    fitnesses = dask.compute(*results)
    return fitnesses
'''
def visit_files(fileList):
    '''
    filter files into useful sub categories
    '''
    resting_heart_rate = []
    moderately_active = []
    very_active_minutes = []
    for input_file in tqdm(fileList,title='Loading in massive everything data set'):
        if "resting_heart_rate" in input_file:
            resting_heart_rate.append(input_file)
        if "moderately_active_minutes" in input_file:
            moderately_active.append(input_file)
        if "very_active_minutes" in input_file:
            very_active_minutes.append(input_file)
    return (very_active_minutes,moderately_active,resting_heart_rate)

def process_fitbit_other_data(list_of_lists):
    '''
    visit files from subcategories build large frames via concatonation.
    '''
    dict_of_frames = {}
    list_of_frames = []
    for list_of_files in list_of_lists:
        for input_file in list_of_files:
            input_df = pd.read_json(input_file)
            dict_of_frames[input_file] = input_df
    return dict_of_frames

            #if cnt>0:
            #    df = pd.concat([df, input_df], axis =1)
            #else:
            #    df = input_df
            #cnt+=1
        #st.write(reduced_df.describe())
        #progress_bar.progress(cnt/len(list_of_lists)*)
        #status_text.text("Data Reading %i%% Complete" % float(cnt/len(list_of_lists)))    
        
