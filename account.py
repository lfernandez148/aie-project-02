# User Account

import streamlit as st


def app():
    st.header('Account')

    st.markdown("##### User Profile")
    
    st.markdown(f"User: {st.session_state.user}")
    st.markdown(f"Email: {st.session_state.email}")

