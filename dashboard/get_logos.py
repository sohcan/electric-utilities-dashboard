#logos
import os
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))

def get_logos(directory= HERE, filename=None, current_theme = st.context.theme.type):
    if filename:
        file_loc = {
            'Dark': os.path.join(directory, filename)
            }
        logo_path = file_loc['Dark']
        
        return logo_path
    else:
        file_loc = {
            'Dark': os.path.join(directory,"images/NTNG_Logo_Dark.png"),
            'Light': os.path.join(directory,"images/NTNG_Logo_Light.png")
            } 

        if current_theme == "dark":
            logo_path = file_loc['Dark'] # White text for dark backgrounds
        else:
            logo_path = file_loc['Light'] # Black text for light backgrounds

        return logo_path

#st.logo(logo_path, size="large")
#st.image(logo_path, width=200, )