#!/usr/bin/env python3
"""
API Endpoints Diagram for Campaign Performance Assistant
"""

from diagrams import Diagram, Cluster
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.generic.database import SQL
from diagrams.onprem.client import Client

# Create the diagram
with Diagram("Campaign Performance Assistant - API Endpoints", 
             show=False, 
             filename="api_endpoints",
             direction="TB"):
    
    # Client
    client = Client("API Client")
    
    # FastAPI Application
    with Cluster("FastAPI Application"):
        fastapi = FastAPI("FastAPI Server")
        
        # Health Endpoints
        with Cluster("Health Endpoints"):
            root_health = Python("/")
            health_endpoint = Python("/health")
        
        # Campaign Endpoints
        with Cluster("Campaign Endpoints"):
            get_campaign = Python("/campaigns/{id}")
            get_top = Python("/campaigns/top/{metric}")
            get_summary = Python("/campaigns/summary")
            get_topic = Python("/campaigns/topic/{topic}")
            get_segment = Python("/campaigns/segment/{segment}")
            compare_campaigns = Python("/campaigns/compare/{id1}/{id2}")
            get_all = Python("/campaigns/all")
        
        # Documentation
        with Cluster("Documentation"):
            swagger = Python("/docs")
            redoc = Python("/redoc")
    
    # Database
    with Cluster("Database"):
        sqlite = SQL("SQLite DB")
    
    # Authentication
    with Cluster("Security"):
        auth = Python("API Key Auth")
        rate_limit = Python("Rate Limiting")
    
    # Connections
    client >> fastapi
    
    # Health endpoints
    fastapi >> root_health
    fastapi >> health_endpoint
    
    # Campaign endpoints
    fastapi >> get_campaign
    fastapi >> get_top
    fastapi >> get_summary
    fastapi >> get_topic
    fastapi >> get_segment
    fastapi >> compare_campaigns
    fastapi >> get_all
    
    # Documentation
    fastapi >> swagger
    fastapi >> redoc
    
    # Security
    get_campaign >> auth
    get_top >> auth
    get_summary >> auth
    get_topic >> auth
    get_segment >> auth
    compare_campaigns >> auth
    get_all >> auth
    
    auth >> rate_limit
    rate_limit >> sqlite 