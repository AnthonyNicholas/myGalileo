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
    if API_TOKEN:
        st.text("API TOKEN is"+ str(API_TOKEN))
        URL = "https://api.fitbit.com/1.2/user/~/sleep/date/2020-08-18.json"
        responses = requests.request("GET",url,data=payload,headers=headers)
        st.text(responses)
    radio_value = st.sidebar.radio("\
		Are you more interested in Sleep/Exercise/the interplay between them"
		,["Sleep","Exercise","Interplay"])
    # radio_value = st.sidebar.radio("Target Number of Samples",[10,20,30])
