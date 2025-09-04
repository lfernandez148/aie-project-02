# Campaign Performance Assistant - Chat Interface

import streamlit as st
from chatbot import chat_query, clear_memory, get_memory_stats
from chart_utils import display_chart
import pandas as pd
import login

# Sample questions and help message (should match chatbot.py)
SAMPLE_QUESTIONS = [
    "Show executive summary for campaign 101",
    "Provide summary statistics for all campaigns",
    "Provide top 10 performing campaigns",
    "Show average open rate for all campaigns",
    "Display bar chart of audience volume by topic",
    "Display conversion rate trends over time",
]

HELP_MESSAGE = "Examples of requests you can make:"


def get_username():
    """Get the current username from session state, fallback to 'default'."""
    user_info = login.get_current_user()
    return user_info['username'] if user_info else "default"


def get_thread_id():
    """Get current thread ID (using username for now)."""
    return get_username()


def get_user_id():
    """Get current user ID from session state."""
    return st.session_state.get('user_id', None)


def app():
    st.title("Campaign Performance Assistant")
    st.markdown(
        """
        I have access to your Campaign Performance Reports and Campaigns Database.  
        I can assist you in retrieving and presenting the information you want.
        """
    )

    # Show sample questions as a static list below the intro
    st.markdown(f"**{HELP_MESSAGE}**")
    st.markdown("\n".join([f"- {q}" for q in SAMPLE_QUESTIONS]))

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
                st.dataframe(
                    pd.DataFrame(table["rows"], columns=table["columns"])
                )
            if message.get("examples"):
                st.markdown("\n".join([f"- {q}" for q in message["examples"]]))
            # Display source information if available
            if message.get("source"):
                st.caption(f"📚 Source: {message['source']}")

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
                response = chat_query(prompt, get_thread_id(), get_user_id())
            if isinstance(response, dict) and response.get("type") == "chart":
                st.markdown(response.get("message", ""))
                data = response.get("data", {})
                display_chart(data.get("chart_type"))
                if data.get("source"):
                    st.caption(f"📚 Source: {data['source']}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data.get("message", ""),
                    "chart_type": data.get("chart_type", None),
                    "source": data.get("source", "")
                })
            elif isinstance(response, dict) and response.get("type") == "table":
                st.markdown(response.get("message", ""))
                data = response.get("data", {})
                st.dataframe(
                    pd.DataFrame(data.get("rows",[]), columns=data.get("columns",[]))
                )
                if data.get("source"):
                    st.caption(f"📚 Source: {data['source']}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get("message", ""),
                    "table_data": {
                        "columns": data.get("columns", []),
                        "rows": data.get("rows", [])
                    },
                    "source": data.get("source", "")
                })
            elif isinstance(response, dict) and response.get("type") == "error":
                st.error(response.get("message", "Unknown error."))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get("message", "Unknown error.")
                })
            elif isinstance(response, dict) and response.get("type") == "text":
                st.markdown(response.get("message", ""))
                if response.get("source"):
                    st.caption(f"📚 Source: {response['source']}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get("message", ""),
                    "source": response.get("source", "")
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
                clear_memory(get_thread_id(), get_user_id())
                st.session_state.messages = []
                st.rerun()
