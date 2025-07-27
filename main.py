# Main - Streamlit App entry point

import streamlit as st
from streamlit_option_menu import option_menu
import home
import account
import admin

st.set_page_config(
    page_title="CPAssist",
)

if "user" not in st.session_state:
    st.session_state.user = "admin"
    st.session_state.email = "admin@my_company.com"


def run():
    with st.sidebar:
        app = option_menu(
            menu_title='CPAssist',
            options=['Home', 'Account', 'Admin'],
            icons=['house-fill', 'person-circle', 'trophy-fill'],
            menu_icon='',
            default_index=0,
            styles={
                "container": {
                    "padding": "5!important",
                    "background-color": "white"
                },
                "icon": {"color": "green", "font-size": "23px"},
                "nav-link": {
                    "color": "black",
                    "font-size": "20px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#cccccce6"
                },
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )
    if app == "Home":
        home.app()
    if app == "Account":
        account.app()
    if app == 'Admin':
        admin.app()


run()            
