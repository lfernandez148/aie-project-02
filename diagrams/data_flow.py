#!/usr/bin/env python3
"""
Data Flow Diagram for Campaign Performance Assistant
"""

from diagrams import Diagram, Cluster
from diagrams.programming.language import Python
from diagrams.programming.framework import FastAPI
from diagrams.generic.database import SQL
from diagrams.generic.storage import Storage
from diagrams.generic.network import Firewall
from diagrams.onprem.client import Client
from diagrams.generic.compute import Rack

# Create the diagram
with Diagram("Campaign Performance Assistant - Data Flow", 
             show=False, 
             filename="data_flow",
             direction="LR"):
    
    # User Input
    user = Client("User Query")
    
    # Frontend
    with Cluster("Frontend"):
        streamlit = Python("Streamlit UI")
    
    # Processing Layer
    with Cluster("Processing Layer"):
        langchain = Python("LangChain")
        llm = Python("OpenAI/LM Studio")
        tools = Python("LLM Tools")
    
    # Data Sources
    with Cluster("Data Sources"):
        fastapi = FastAPI("FastAPI")
        chroma = Storage("ChromaDB")
        sqlite = SQL("SQLite DB")
        docs = Storage("Documents")
    
    # Services
    with Cluster("Services"):
        auth = Firewall("Auth")
        rate_limit = Rack("Rate Limiting")
        logging = Python("Logging")
    
    # External
    with Cluster("External"):
        grafana = Python("Grafana Loki")
        langsmith = Python("LangSmith")
    
    # Data Flow
    user >> streamlit
    streamlit >> langchain
    langchain >> llm
    langchain >> tools
    
    tools >> fastapi
    tools >> chroma
    
    fastapi >> auth
    auth >> rate_limit
    rate_limit >> sqlite
    
    docs >> chroma
    
    langchain >> logging
    logging >> grafana
    langchain >> langsmith
    
    # Response Flow
    llm >> streamlit
    tools >> streamlit
    fastapi >> streamlit
    chroma >> streamlit 