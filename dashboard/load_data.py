#Importing Raw, Quick sort by Meter Date
import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data(directory, filename, kwh=False, **kwargs):
    where = os.path.join(directory,filename)
    if kwh==True:
        df = pd.read_csv(where, parse_dates=['Date'], **kwargs)
        df.sort_values(by=['Meter','Date'], inplace = True)
        df.reset_index(inplace=True, drop=True)
    else:
        df = pd.read_csv(where)
    return df