import streamlit as st

def render_info_banner():
    """
    CSS to force an INFO banner at the absolute top of the Streamlit web application.
    """
    banner_html = """
    <style>
        /* Top Banner Only */
        .info-banner-top {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #2b313e; /* Neutral Dark Slate */
            color: #f8f9fa;
            text-align: center;
            font-family: "Source Sans Pro", sans-serif;
            font-weight: 600;
            font-size: 0.75rem;
            letter-spacing: 0.08rem; 
            padding: 0.25rem 0;
            z-index: 999999;
            opacity: 0.75;
        }

        /* Push only the TOP of the main content down */
        .block-container {
            padding-top: 3.5rem !important;
        }
        
        /* Adjust the Streamlit Header (Hamburger menu) */
        header[data-testid="stHeader"] {
            top: 25px !important; 
        }
        
        /* Adjust the Sidebar */
        section[data-testid="stSidebar"] {
            top: 25px !important;
        }
    </style>
    
    <div class="info-banner-top">SYNTHETIC UNDER CONSTRUCTION INFORMATION (SUCI)</div>
    """    
    st.markdown(banner_html, unsafe_allow_html=True)
