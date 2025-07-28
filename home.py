# Campaign Performance Assistant - Chat Interface

import streamlit as st
from chatbot import chat_query, clear_memory
from chart_utils import display_chart
import pandas as pd


def app():
    st.title("Campaign Performance Assistant")
    st.write(
        "Ask me anything about your campaign data! "
        "(I can only answer questions about your campaigns.)"
        )

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history (show text, charts, tables, and examples)
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "✨"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message.get("chart_type"):
                display_chart(message["chart_type"])
            if message.get("table_data"):
                table = message["table_data"]
                st.dataframe(pd.DataFrame(table["rows"], columns=table["columns"]))
            if message.get("examples"):
                st.markdown("\n".join([f"- {q}" for q in message["examples"]]))

    # Chat input
    prompt = st.chat_input("Ask about your campaign data...")
    
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Display assistant response
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Thinking..."):
                response = chat_query(prompt)
            if isinstance(response, dict) and response.get("type") == "chart":
                st.markdown(response.get("message", ""))
                display_chart(response.get("chart_type"))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get("message", ""),
                    "chart_type": response.get("chart_type", None)
                })
            elif isinstance(response, dict) and response.get("type") == "table":
                st.markdown(response.get("message", ""))
                st.dataframe(pd.DataFrame(response["rows"], columns=response["columns"]))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get("message", ""),
                    "table_data": {
                        "columns": response["columns"],
                        "rows": response["rows"]
                    }
                })
            elif isinstance(response, dict) and response.get("type") == "examples":
                st.markdown(response.get("message", ""))
                st.markdown("\n".join([f"- {q}" for q in response.get("examples", [])]))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get("message", ""),
                    "examples": response.get("examples", [])
                })
            elif isinstance(response, dict) and response.get("type") == "error":
                st.error(response.get("message", "Unknown error."))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get("message", "Unknown error.")
                })
            else:
                st.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

    # Add memory management buttons
    if st.session_state.messages:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("Clear Chat History", type="secondary"):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("Clear Memory", type="secondary"):
                clear_memory()
                st.success("Memory cleared! The assistant will start fresh.")
        

