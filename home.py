# Campaign Performance Assistant - Chat Interface

import streamlit as st
from chatbot import chat_query, clear_memory


def app():
    st.title("Campaign Performance Assistant")
    st.write(
        "Ask me anything about your campaign data! "
        "(I can only answer questions about your campaigns.)"
        )

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "✨"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

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
            st.markdown(response)
        
        # Add assistant response to chat history
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
        

