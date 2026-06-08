import streamlit as st
import pandas as pd

@st.cache_data
def get_chart_data(df: pd.DataFrame, meter, col='Meter', col_filter='Observed'):
    chart_data = df[df[col]==meter] #[['Date','Observed','Seasonal','Residual','Forecast','Trend','mean']]
    idx = chart_data[col_filter].dropna().tail(1).index; idd = chart_data[col_filter].dropna().tail(1)
    cont_forecast = pd.DataFrame(
        {
            'Date': chart_data['Date'],
            'Observed': chart_data[col_filter].round(decimals=0).astype('Int64'),
            'Forecast': chart_data['Forecast'].round(decimals=0).astype('Int64'),
            'Modeled': chart_data['mean'].round(decimals=0).astype('Int64'),
            }
    )
    cont_forecast.loc[idx,'Forecast'] = idd
    return chart_data, cont_forecast, cont_forecast.loc[idx]