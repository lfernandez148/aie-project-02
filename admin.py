# Admin / Settings

import streamlit as st


def app():
    st.header('Admin')

    st.markdown("##### LLM Setings:")
    st.session_state.llm_temperature_for_qtns_generation = st.slider(
        "Temperature for Question Geneartion:",
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        value=0.3
    )