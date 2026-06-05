import streamlit as st

def multi_meter_select(location_df, radio_search_col_dict, radio_col_key, search, show_anyway = False):
    search_df = location_df[location_df[radio_search_col_dict[radio_col_key]] == search]
    if (len(search_df) <= 1) and (show_anyway != True):
        meter_row = st.dataframe(data= search_df, hide_index=True, on_select= 'rerun', selection_mode="single-row", selection_default= {'selection': {'rows': [0]}})
        st.session_state['meter_row'] = search_df.iloc[meter_row.selection.rows[0]]
        st.session_state['meter'] = search_df.iloc[meter_row.selection.rows[0]]['Meter'].item()
        st.session_state.length_sdf = len(search_df)
        st.rerun()
    elif (len(search_df) > 1) or (show_anyway == True):
        meter_row = dialog(search_df)

@st.dialog("Meters at Location", width="large")
def dialog(search_df):
    st.markdown('Multiple meters are present at this location (Select One)')
    meter_row = st.dataframe(data= search_df, hide_index=True, on_select="rerun", selection_mode="single-row", selection_default= {'selection': {'rows': [0]}})
    st.session_state.meter_row = search_df.iloc[meter_row.selection.rows[0]]
    st.session_state.meter = search_df.iloc[meter_row.selection.rows[0]]['Meter'].item()
    st.session_state.length_sdf = len(search_df)
    close_dialog = st.button('Confirm')
    if close_dialog:
        st.rerun()