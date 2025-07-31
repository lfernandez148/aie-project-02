#!/usr/bin/env python3
"""
Tool Selection Flow Diagram for Campaign Performance Assistant
"""

from diagrams import Diagram, Cluster
from diagrams.programming.language import Python
from diagrams.generic.database import SQL
from diagrams.generic.storage import Storage
from diagrams.programming.framework import FastAPI
from diagrams.onprem.client import Client

# Create the diagram
with Diagram("Campaign Performance Assistant - Tool Selection Flow", 
             show=False, 
             filename="tool_selection_flow",
             direction="TB"):
    
    # User Input
    user = Client("User Query")
    
    # LLM Processing
    with Cluster("LLM Processing"):
        langchain = Python("LangChain")
        llm = Python("OpenAI/LM Studio")
    
    # Tool Selection
    with Cluster("Tool Selection"):
        tool_selector = Python("Tool Selection")
    
    # Available Tools
    with Cluster("Available Tools"):
        search_docs = Python("search_campaign_documents")
        get_campaign = Python("get_campaign_by_id")
        get_top = Python("get_top_campaigns_by_metric")
        get_topic = Python("get_campaigns_by_topic")
        get_segment = Python("get_campaigns_by_segment")
        get_stats = Python("get_campaign_summary_stats")
        compare = Python("compare_campaigns_by_id")
        create_chart = Python("create_campaign_chart")
    
    # Data Sources
    with Cluster("Data Sources"):
        fastapi = FastAPI("FastAPI")
        chroma = Storage("ChromaDB")
        sqlite = SQL("SQLite DB")
    
    # Response Types
    with Cluster("Response Types"):
        text_response = Python("Text Response")
        table_response = Python("Table Response")
        chart_response = Python("Chart Response")
        error_response = Python("Error Response")
    
    # Flow
    user >> langchain
    langchain >> llm
    llm >> tool_selector
    
    # Tool Selection Paths
    tool_selector >> search_docs
    tool_selector >> get_campaign
    tool_selector >> get_top
    tool_selector >> get_topic
    tool_selector >> get_segment
    tool_selector >> get_stats
    tool_selector >> compare
    tool_selector >> create_chart
    
    # Tool to Data Source
    search_docs >> chroma
    get_campaign >> fastapi
    get_top >> fastapi
    get_topic >> fastapi
    get_segment >> fastapi
    get_stats >> fastapi
    compare >> fastapi
    create_chart >> fastapi
    
    fastapi >> sqlite
    
    # Response Flow
    search_docs >> text_response
    get_campaign >> text_response
    get_topic >> text_response
    get_segment >> text_response
    get_stats >> text_response
    compare >> text_response
    
    get_top >> table_response
    create_chart >> chart_response
    
    # Error handling
    search_docs >> error_response
    get_campaign >> error_response
    get_top >> error_response
    get_topic >> error_response
    get_segment >> error_response
    get_stats >> error_response
    compare >> error_response
    create_chart >> error_response 