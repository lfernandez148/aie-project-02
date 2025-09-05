# Campaign Performance Assistant - Chat Interface

import streamlit as st
from chatbot import chat_query, clear_memory, get_memory_stats, token_tracker
from chart_utils import display_chart
import pandas as pd
import login
import json

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


def load_chat_history():
    """Load chat history from database for current user and thread."""
    user_id = get_user_id()
    thread_id = get_thread_id()
    
    if user_id and thread_id:
        try:
            history = token_tracker.get_chat_history(user_id, thread_id, limit=100)
            return history
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
            return []
    return []


def save_chat_message(role: str, content: str, response_type: str = "text", 
                     chart_type: str = None, table_data: dict = None, source: str = None):
    """Save a chat message to the database."""
    user_id = get_user_id()
    thread_id = get_thread_id()
    
    if user_id and thread_id:
        try:
            # Convert table_data to JSON string if provided
            table_data_json = json.dumps(table_data) if table_data else None
            
            token_tracker.save_chat_message(
                user_id=user_id,
                thread_id=thread_id,
                role=role,
                content=content,
                response_type=response_type,
                chart_type=chart_type,
                table_data=table_data_json,
                source=source if source and source.strip() else None
            )
        except Exception as e:
            st.error(f"Error saving chat message: {e}")


def clear_persistent_chat_history():
    """Clear persistent chat history from database."""
    user_id = get_user_id()
    thread_id = get_thread_id()
    
    if user_id and thread_id:
        try:
            result = token_tracker.clear_chat_history(user_id, thread_id)
            return result.get("status") == "success"
        except Exception as e:
            st.error(f"Error clearing chat history: {e}")
            return False
    return False


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
        
        # Load persistent chat history for authenticated users
        user_id = get_user_id()
        if user_id:
            persistent_history = load_chat_history()
            if persistent_history:
                st.session_state.messages = persistent_history
                st.success(f"Loaded messages from your chat history")

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
            # Display source information if available and not empty
            source = message.get("source", "")
            if source and source.strip():
                st.caption(f"📚 Source: {source}")

    # Chat input
    prompt = st.chat_input("Ask about your campaign data...")
    
    if prompt:
        # Add user message to chat history
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        
        # Save user message to database
        save_chat_message("user", prompt, "text")
        
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
                source = data.get("source", "")
                if source and source.strip():
                    st.caption(f"📚 Source: {source}")
                
                # Add to session state
                assistant_message = {
                    "role": "assistant",
                    "content": data.get("message", ""),
                    "chart_type": data.get("chart_type", None),
                    "source": source if source and source.strip() else ""
                }
                st.session_state.messages.append(assistant_message)
                
                # Save to database
                save_chat_message(
                    "assistant", 
                    data.get("message", ""), 
                    "chart",
                    chart_type=data.get("chart_type"),
                    source=source if source and source.strip() else None
                )
            elif isinstance(response, dict) and response.get("type") == "table":
                st.markdown(response.get("message", ""))
                data = response.get("data", {})
                st.dataframe(
                    pd.DataFrame(data.get("rows",[]), columns=data.get("columns",[]))
                )
                source = data.get("source", "")
                if source and source.strip():
                    st.caption(f"📚 Source: {source}")
                
                # Add to session state
                table_data = {
                    "columns": data.get("columns", []),
                    "rows": data.get("rows", [])
                }
                assistant_message = {
                    "role": "assistant",
                    "content": response.get("message", ""),
                    "table_data": table_data,
                    "source": source if source and source.strip() else ""
                }
                st.session_state.messages.append(assistant_message)
                
                # Save to database
                save_chat_message(
                    "assistant", 
                    response.get("message", ""), 
                    "table",
                    table_data=table_data,
                    source=source if source and source.strip() else None
                )
            elif isinstance(response, dict) and response.get("type") == "error":
                st.error(response.get("message", "Unknown error."))
                
                # Add to session state
                assistant_message = {
                    "role": "assistant",
                    "content": response.get("message", "Unknown error.")
                }
                st.session_state.messages.append(assistant_message)
                
                # Save to database
                save_chat_message(
                    "assistant", 
                    response.get("message", "Unknown error."), 
                    "error"
                )
            elif isinstance(response, dict) and response.get("type") == "text":
                st.markdown(response.get("message", ""))
                source = response.get("source", "")
                if source and source.strip():
                    st.caption(f"📚 Source: {source}")
                
                # Add to session state
                assistant_message = {
                    "role": "assistant",
                    "content": response.get("message", ""),
                    "source": source if source and source.strip() else ""
                }
                st.session_state.messages.append(assistant_message)
                
                # Save to database
                save_chat_message(
                    "assistant", 
                    response.get("message", ""), 
                    "text",
                    source=source if source and source.strip() else None
                )
            else:
                st.markdown(response)
                
                # Add to session state
                assistant_message = {
                    "role": "assistant",
                    "content": response
                }
                st.session_state.messages.append(assistant_message)
                
                # Save to database
                save_chat_message("assistant", str(response), "text")

    # Add memory management buttons
    if st.session_state.messages:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("Clear Chat History", type="secondary"):
                # Clear LangGraph memory
                clear_memory(get_thread_id(), get_user_id())
                
                # Clear persistent chat history from database
                if clear_persistent_chat_history():
                    st.success("Chat history cleared from database")
                
                # Clear session state
                st.session_state.messages = []
                st.rerun()
