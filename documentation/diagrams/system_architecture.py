#!/usr/bin/env python3
"""
System Architecture Diagram for Campaign Performance Assistant
"""

from diagrams import Diagram, Cluster
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.generic.network import Firewall
from diagrams.generic.compute import Rack
from diagrams.generic.storage import Storage
from diagrams.generic.database import SQL
from diagrams.onprem.client import Client
from diagrams.generic.device import Mobile

# Create the diagram
with Diagram("Campaign Performance Assistant - System Architecture", 
             show=False, 
             filename="system_architecture",
             direction="TB"):
    
    # User Interface Layer
    with Cluster("Frontend Layer"):
        streamlit = Python("Streamlit UI")
        mobile = Mobile("Mobile Access")
        client = Client("Web Browser")
    
    # Backend Layer
    with Cluster("Backend Layer"):
        fastapi = FastAPI("FastAPI")
        langchain = Python("LangChain")
        llm = Python("OpenAI/LM Studio")
    
    # Data Layer
    with Cluster("Data Layer"):
        sqlite = SQL("SQLite DB")
        chroma = Storage("ChromaDB")
        docs = Storage("Documents")
    
    # Services Layer
    with Cluster("Services Layer"):
        auth = Firewall("Authentication")
        rate_limit = Rack("Rate Limiting")
        logging = Python("Loguru + Loki")
    
    # External Services
    with Cluster("External Services"):
        grafana = Python("Grafana Loki")
        langsmith = Python("LangSmith")
    
    # Connections
    streamlit >> fastapi
    mobile >> fastapi
    client >> fastapi
    
    fastapi >> auth
    auth >> rate_limit
    rate_limit >> sqlite
    
    langchain >> llm
    langchain >> chroma
    langchain >> fastapi
    
    docs >> chroma
    
    logging >> grafana
    langchain >> langsmith 