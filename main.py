# Main - Streamlit App entry point

import streamlit as st
from streamlit_option_menu import option_menu
import home
import account
import admin
import login  # Import the login module

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def run_authenticated_app():
    """Run the main application for authenticated users."""
    st.set_page_config(
        page_title="CPAssist",
    )
    
    # Get current user info
    user_info = login.get_current_user()
    
    with st.sidebar:
        # User info display
        st.markdown(f"User: {user_info['email']}")
        
        # Main navigation
        app = option_menu(
            menu_title='CPAssist',
            options=['Home', 'Account', 'Admin', 'Logout'],
            icons=['house-fill', 'person-circle', 'trophy-fill', 'door-open'],
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
    
    # Route to appropriate page
    if app == "Home":
        home.app()
    elif app == "Account":
        account.app()
    elif app == 'Admin':
        # Check if user has admin role
        if user_info['role'] == 'admin':
            admin.app()
        else:
            st.error("Access denied. Admin privileges required.")
            st.info("Contact your administrator for access.")
    elif app == 'Logout':
        login.logout()

def run():
    """Main application entry point."""
    # Check authentication
    if not login.check_authentication():
        # Show login page
        login.login_page()
    else:
        # Show main application
        run_authenticated_app()

if __name__ == "__main__":
    run()