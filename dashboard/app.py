import os.path

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta, date
from scipy import stats

from load_data import load_data
from get_logos import get_logos
from clean_data import clean_data
from load_card_data import load_installation_data
from load_chart_data import get_chart_data
from load_select_dialog_loc import multi_meter_select
from banner import render_info_banner

from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.forecasting.stl import STLForecast

import streamlit as st
import altair as alt

st.set_page_config(
    page_title="NTNG Electric Utility",
    page_icon=":material/fort:",
    initial_sidebar_state="expanded",
    layout="wide"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            }
            h1 {
                letter-spacing: -0.03em;
            }
            div[data-testid="stMarkdownContainer"] p {
                line-height: 1.45;
                }
    </style>
    """,
    unsafe_allow_html=True
)


render_info_banner()

HERE = os.path.dirname(os.path.abspath(__file__))
logo_path = get_logos(current_theme = st.context.theme.type)

mloc = load_data(HERE, "data_synthetic/Utilities_Fun_Loc.csv")

#st.logo(logo_path, size="large")

if 'thresh_key' not in st.session_state:
    st.session_state['thresh_key'] = 1.0

if 'fxct_key' not in st.session_state:
    st.session_state['fxct_key'] = 6

if 'meter_row' not in st.session_state:
    st.session_state['meter_row'] = None

if 'search_last' not in st.session_state:
    st.session_state['search_last'] = None

if 'meter' not in st.session_state:
    st.session_state['meter'] = mloc['Meter'].iloc[0]

if 'length_sdf' not in st.session_state:
    st.session_state['length_sdf'] = 0

if 'kWh' not in st.session_state:
    st.session_state['kWh'] = load_data(HERE,"data_synthetic/Utilities_Fun.csv", kwh=True)

if 'animate' not in st.session_state:
    st.session_state['animate'] = True

#else:
    #st.session_state['meter'] = st.session_state['meter_row']['Observed']

#if 'new_reading' not in st.session_state:
#    st.session_state['new_reading'] = pd.DataFrame({'Meter':[],'Date':[],'KWH':[],'USD':[]})


#meter_sel = st.container()
#outlier_sel = st.container()
#fxct_sel = st.container(border=True)

kWh = st.session_state['kWh']
nkWh = clean_data(kWh, fxct_count=st.session_state.fxct_key, ol_thresh=st.session_state.thresh_key)

st.space(size="medium")

meter = st.session_state['meter']

loc_data = mloc[mloc.Meter == meter]

cd_KWH = load_installation_data(nkWh, col='KWH')
cd_USD = load_installation_data(nkWh, col='USD')
cd_TRN = load_installation_data(nkWh, col='Trend')
cd_MCO = load_installation_data(nkWh, col='KWH',sum_rows=False)

chart_data, cont_forecast, cf_last= get_chart_data(nkWh, meter=meter)

if 'new_reading' not in st.session_state:
    st.session_state['new_reading'] = pd.DataFrame({'Meter':[],'Date':[],'KWH':[],'USD':[]})
    st.session_state['new_reading'].Meter = meter
    st.session_state['new_reading'].KWH = cf_last.Observed
    st.session_state['new_reading'].Date = cf_last.Date

first_index = 0; current_index = -2; last_index = -1


st.title("Energy Signal")
st.subheader("Electrical awareness and forecasting.")

tab1, tab2, tab3 = st.tabs(["Installation 550XA", f"{loc_data['Location'].item()}" , "Add Items"], on_change='rerun')
metrics_sb = st.sidebar.container(border=True, height='content')
disclmr_sb = st.sidebar.container(border=True, height='content')

if tab1.open == True:
    
    with tab1:
        st.markdown("""*This view provides aggregate indicators for total institutional energy usage and data integrity over time. Expand sidebar for details.*""")
        agg_0, agg_1 = st.columns([.5,.5])

        with metrics_sb:
            image_0 = st.image(logo_path, width=200, caption="")

            st.markdown('''***Installation Metrics***  
                Aggregated measures of cost, demand, and current data set across the NTSNG Virtual Installation''')

            st.markdown(f'''Tab **Installation 550XA** is the current tab.''')
            st.markdown(f'''Tab **{loc_data['Location'].item()}** shows meter {meter} data, use dropdown below to change.''')     
    
            st.markdown(f'''Tab **Add Items** allows for inputting more meter readings for {meter}''')
            with st.popover("Select Meter", width="content"):
                find_meter_options = {"Utility Name":'Utility_Company', "Account #":'Account',"Service Address":'Service_Address', "Meter":'Meter_Char', "Location":'Location'}
                loc_dat_col = st.radio("Find meter by:", options = (find_meter_options), index=4)
                search = st.selectbox('Click or Start Typing...', mloc[find_meter_options[loc_dat_col]].unique(), placeholder="None")

                if search and (search != st.session_state.search_last):
                    st.session_state.search_last = search
                    multi_meter_select(mloc, find_meter_options, loc_dat_col, search)
                
                re_show_multi_meter_select = st.button('Meters')

                if re_show_multi_meter_select:
                    multi_meter_select(mloc, find_meter_options, loc_dat_col, search, show_anyway=True)
                    #search_df = multi_meter_select(mloc, find_meter_options, loc_dat_col, search)              
        with disclmr_sb:
            st.markdown("""**The North Takoma Space National Guard** *is composed of wholly-synthetic but 'plausible sounding': locations, variable types, variable quantities, costs, and nominal descriptions.*""")
        st.space(size="small")
    
        with agg_0:
            st.metric(
                "Installation Energy Usage",
                f"{cd_KWH.iloc[current_index].round():,.0f} kWh",
                f"{((cd_KWH.iloc[current_index]-cd_KWH.mean())/cd_KWH.mean())*100:.2f}%",
                help=r"$D_t = \frac{E_t - \bar{E}}{\bar{E}}$",
                chart_data=cd_KWH,
                chart_type="area",
                border=True,
                delta_description= f"{cd_USD.index[current_index].strftime('%b')} {cd_USD.index[current_index].strftime('%Y')} : "
            )

            st.metric(
                "Total Energy Cost",
                f"${cd_USD.iloc[current_index]:,.2f}",
                f"{((cd_USD.iloc[current_index]-cd_USD.mean())/cd_USD.mean())*100:.2f}%",
                help=r"$\Delta C_t = \frac{C_t - \bar{C}}{\bar{C}}$",
                chart_data=cd_USD,
                chart_type="area",
                border=True,
                delta_description= f"{cd_USD.index[current_index].strftime('%b')} {cd_USD.index[current_index].strftime('%Y')}"
            )


        with agg_1:

            st.metric(
                "Meter Reading Count",
                f"{cd_MCO.iloc[last_index].round():,.0f} Recorded",
                f"{(cd_MCO.iloc[last_index] - cd_MCO.iloc[current_index]) :.0f}",
                help=r"$\Delta N_t = N_t - N_{t-1}$",
                chart_data=cd_MCO,
                chart_type="bar",
                border=True,
                delta_description= f"{cd_USD.index[last_index].strftime('%b')} {cd_USD.index[last_index].strftime('%Y')}"
            )

            st.metric(
                "Blended Rate:",
                f"${(cd_USD.sum()/cd_KWH.sum()):.3f}/KWh",
                help=r"$R = \frac{\sum C}{\sum E}$",
                chart_data=cd_USD/cd_KWH,
                chart_type="bar",
                border=True,
                delta_description= f"{cd_USD.index[current_index].strftime('%b')} {cd_USD.index[current_index].strftime('%Y')}",
            )

    st.metric(
        "Total Energy Trend",
        f"{cd_TRN.iloc[current_index].round():,.0f} kWh", # "${(cd_USD.sum()/cd_KWH.sum().round())*cd_KWH.iloc[current_index].sum() - (cd_USD.sum().round()/cd_KWH.sum().round())*cd_KWH.mean() :,.2f}" ,
        f"{((cd_TRN.iloc[current_index]-cd_TRN.mean())/cd_TRN.mean())*100:.2f}%",
        help=r"$\Delta T_t = \frac{T_t - \bar{T}}{\bar{T}}$",
        chart_data=cd_TRN.iloc[first_index:current_index],
        chart_type="line",
        border=True,
        delta_description= f"{cd_TRN.index[first_index].strftime('%b')} {cd_TRN.index[first_index].strftime('%y')} - {cd_TRN.index[current_index].strftime('%b')} {cd_TRN.index[current_index].strftime('%y')}"
    )


if tab2.open == True:
    
    with tab2:
        st.markdown("""*This view provides forecasting and summary information for a specific location and utility-provider.* 
                    *Adjust* Forecast Length, Error Threshold (Flagged Readings) *or change* Meter *by expanding sidebar, making selections and submitting* Recast""")
        st.table(loc_data[['Utility_Company','Meter','Location','Service_Address','Account']].rename(columns=lambda x: x.replace('_', ' '))) 


        with metrics_sb:
            image_0 = st.image(logo_path, width=200)
            st.markdown('''**Site Metrics**  
            Breakdown of meter readings with a seasonal decomposition, trends and notable outliers are predicted.''')
            st.markdown('''*Caution:* forecasting with less than 24 months of observation may be insufficient for reasonable analyses.''')
           
        st.space(size="small")

        #site_sb_shart = st.sidebar.container(border=True, horizontal=False, height='content')
        site_sb_fcxt = st.sidebar.container(border=True, horizontal=True, height='content')
        site_sb_select = st.sidebar.container(border=True, horizontal=False, height='content')

        with site_sb_fcxt:
            with st.form('Recalculate Forecast', border=False):
                st.markdown("Forecast Length:")
                st.select_slider(
                    "Select (how many months):",
                    options= np.arange(1,48),
                    value= 6,
                    key="fxct_key"
                    )
                st.markdown("Error Threshold:")
                st.select_slider(
                    "Select standard deviation scaling:",
                    options= np.arange(1,6.25,.25),
                    value=1,
                    key="thresh_key"
                    )
                re_cast_submit = st.form_submit_button("Recast")
                if re_cast_submit:
                    st.session_state['animate'] = True

        with site_sb_select:
            st.markdown('Additional')
            with st.popover("Select Meter", width="stretch"):
                find_meter_options = {"Utility Name":'Utility_Company', "Account #":'Account',"Service Address":'Service_Address', "Meter":'Meter_Char', "Location":'Location'}
                loc_dat_col = st.radio("Find meter by:", options = (find_meter_options), index=4)
                search = st.selectbox('Click or Start Typing...', mloc[find_meter_options[loc_dat_col]].unique(), placeholder="None")
                if search and (search != st.session_state.search_last):
                    st.session_state.search_last = search
                    multi_meter_select(mloc, find_meter_options, loc_dat_col, search)
                
                re_show_multi_meter_select = st.button('Meter')
                if re_show_multi_meter_select:
                    multi_meter_select(mloc, find_meter_options, loc_dat_col, search, show_anyway=True)

            #with st.popover("Add New Billing Data", width="stretch"):
                #with st.form(key="billing_form", border=False):
                    #new_Date = st.date_input("Meter Read Date", min_value = chart_data[['Date','Observed']].dropna().tail(1).Date.item(), value=chart_data[['Date','Observed']].dropna().tail(1).Date.item())
                    #new_KWH = st.number_input("kWh Used", min_value=0, format="%d")
                    #new_total_cost = st.number_input("Total Cost ($)", min_value=0.0, format="%.2f")
                    #new_read_row = pd.DataFrame({'Meter':[meter],'Date':[new_Date],'KWH':[new_KWH],'USD':[new_total_cost]})
                    #submit_button = st.form_submit_button(label="Save Data")
                    #if submit_button:
                        #st.session_state['new_reading'] = pd.concat([st.session_state['new_reading'], new_read_row], ignore_index=True)


       
    with st.container(border=True):
        fcst_title = st.markdown(f"""**Meter {meter} Forecast**  \nSeasonal-Trend LOESS Decomposition and Forecasting.""")  
        with st.container(border=False):
            fxct_len = st.select_slider(
                "Forecast Length (by month):",
                options = cont_forecast[['Date','Forecast']].dropna(),
                format_func = lambda x: x.strftime('%b %Y'),
                value = cont_forecast['Date'].dropna().tail(1).item(),
                key="fxct_len_key"
                )

        st.space(size="small")

        #obsv_title = st.markdown(f" Energy Use + Trend (kWh)", text_alignment="left")
        #st.dataframe(chart_data[chart_data['Outer']==True])

        fcst_draw = cont_forecast.loc[cont_forecast['Date'] <= fxct_len]
        fart_draw = chart_data[chart_data['Outer']==True][['Date','KWH']]

        chart_forecast = st.empty()

        shart_select = alt.selection_point(nearest=True, on="pointermove", fields=['Date','Observed'], empty=False)

        if st.session_state['animate'] ==  True:

            with chart_forecast:
                for i in range(1,len(fcst_draw) + 1):
                    shart = alt.Chart(fcst_draw.iloc[:i]).encode(x='Date')
                    shart_obsv = shart.mark_line().encode(y='Observed')
                    shart_cast = shart.mark_line(color='red').encode(y='Forecast')
                    shart_legend = shart.mark_line().encode(color=alt.Color('Forecast', type='nominal', title="STL Forecast", scale=alt.Scale(domain=['Observed','New','Forecast'], range=['blue','grey','red'])))

                    st.altair_chart(shart_obsv + shart_cast + shart_legend)
                    time.sleep(0.01)
            st.session_state['animate'] = False

        else:               
             #st.line_chart(cont_forecast.loc[cont_forecast['Date'] <= fxct_len], x = 'Date', y = ['Observed','Forecast'], width="stretch", color=["grey","red"])             
            shart = alt.Chart(fcst_draw).encode(x='Date')

            shart_obsv = shart.mark_line().encode(y='Observed')
            #shart_newt = shart.mark_line(color='grey', strokeDash = [4,2]).encode(y='KWH')
            shart_cast = shart.mark_line(color='red').encode(y='Forecast')             

            shart_liarr = shart.mark_circle(size=80).encode(x='Date', y='Observed', opacity=alt.when(shart_select).then(alt.value(.7)).otherwise(alt.value(0.)))
            shart_slctr = shart.mark_point(opacity=0).encode(x='Date', tooltip=['Date', 'Observed','Forecast']).add_params(shart_select)
            shart_obsvr = shart.mark_circle(size=80).encode(x='Date', y='Observed', opacity=alt.when(shart_select).then(alt.value(.7)).otherwise(alt.value(0.)))
            shart_castr = shart.mark_circle(color='red', size=80).encode(x='Date', y='Forecast', opacity=alt.when(shart_select).then(alt.value(.7)).otherwise(alt.value(0.)))

            shart_legend = shart.mark_line().encode(color=alt.Color('Forecast', type='nominal', title="STL Forecast", scale=alt.Scale(domain=['Observed','New','Forecast'], range=['blue','grey','red'])))

            st.altair_chart(shart_obsv + shart_obsvr + shart_legend + shart_cast + shart_castr + shart_slctr)
            time.sleep(0.01)
        

    chart_left, chart_right = st.columns(2)

    with chart_right:
        with st.container(border=True):
            st.markdown(f""" Seasonality and Account :material/bolt:  \n*Provider: {loc_data['Utility_Company'].item()}*""")
            #{loc_data['Location'].item()}
            st.dataframe(
                loc_data,
                column_config={
                    "Utility_Company": None,
                    "Service_Address": "Service Address",
                    "Meter_Char": None,

                },
                hide_index=True
            )
            chart_seasonal = st.empty()
            chart_seasonal.line_chart(chart_data[chart_data['Seasonal'].notna()], x = 'Date', y = ['Seasonal'])        

    with chart_left:
        with st.container(border=True):
            st.markdown("""**Flagged :material/bolt: Readings**  \n*Error Threshold sifting*""")
            st.dataframe(chart_data[chart_data['Outer']==True],
            column_order=['Date','KWH','USD','Residual','Seasonal','Trend','CDF'],
            column_config={"Date":st.column_config.DateColumn("Date", format="MMM-YYYY"),
            },
            hide_index=True
            )
            scatter_temp = chart_data[chart_data['Residual'].notna()].rename(columns={'Outer':'Flagged'})
            st.scatter_chart(scatter_temp, x='Date', y = 'Residual',  color="Flagged")
    
    st.markdown(f"Meter {meter} Trend")
    with st.container( border=True):
        st.line_chart(chart_data[chart_data['Observed'].notna()], x = 'Date', y = ['Observed','Trend'], color = ['blue','red'], width="stretch") 

    

            #chart_forecast = st.empty()
            #chart_forecast.line_chart(cont_forecast.dropna().loc[cont_forecast['Date'] <= fxct_len], x = 'Date', y = 'Forecast', width="stretch", color="Red")

        #with chart_right:
            #chart_trend = st.empty()
            #chart_trend.line_chart(chart_data[chart_data['Trend'].notna()], x = 'Date', y = ['Trend'])


if tab3.open == True:
    with metrics_sb:
        image_0 = st.image(logo_path, width=200, caption="")
        st.markdown(f'''Currently showing **{loc_data['Location'].item()}** meter **{meter}** data, use dropdown below to change.''')     
        st.markdown(f'''Tab **Add Items** allows for inputting more meter readings for {meter}''')

        with st.popover("Select Meter", width="content"):
            find_meter_options = {"Utility Name":'Utility_Company', "Account #":'Account',"Service Address":'Service_Address', "Meter":'Meter_Char', "Location":'Location'}
            loc_dat_col = st.radio("Find meter by:", options = (find_meter_options), index=4)
            search = st.selectbox('Click or Start Typing...', mloc[find_meter_options[loc_dat_col]].unique(), placeholder="None")
            if search and (search != st.session_state.search_last):
                st.session_state.search_last = search
                multi_meter_select(mloc, find_meter_options, loc_dat_col, search)
            
            re_show_multi_meter_select = st.button('Meters')
            if re_show_multi_meter_select:
                multi_meter_select(mloc, find_meter_options, loc_dat_col, search, show_anyway=True)
                #search_df = multi_meter_select(mloc, find_meter_options, loc_dat_col, search)              
                
        st.space(size="small")

    with tab3:
        with st.form("Add More Data"):
            st.write(f"Location: **{loc_data['Location'].item()}**, Meter:**{meter}**")

            last_date_val = kWh[kWh['Meter']==meter]['Date'].max()
            new_Date = st.date_input("Meter Read Date", value=last_date_val + pd.DateOffset(months=1))
            new_KWH = st.number_input("kWh Used", min_value=0, value=15000, format="%d")
            new_total_cost = st.number_input("Total Cost ($)", min_value=0.0, value=1800.00, format="%.2f") 

            submitted = st.form_submit_button("Submit") 

            if submitted:
                new_read_row = pd.DataFrame(
                    {
                        'Meter': [int(meter)],
                        'Date': [pd.Timestamp(new_Date)],
                        'KWH': [float(new_KWH)],
                        'USD': [float(new_total_cost)]
                        }
                        )   

                st.session_state['kWh'] = pd.concat([st.session_state['kWh'], new_read_row], ignore_index=True)
                st.success(f"New Reading Added for {new_Date.strftime('%-m/%d/%Y')}!")
                time.sleep(1.0)
        st.dataframe((st.session_state['kWh'])[(st.session_state['kWh']).Event_Type != 'Normal'], hide_index=False)
        st.dataframe(st.session_state['kWh'], hide_index=False)
            