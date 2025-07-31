#!/usr/bin/env python3
"""
Document Ingestion Pipeline Diagram for Campaign Performance Assistant
"""

from diagrams import Diagram, Cluster
from diagrams.programming.language import Python
from diagrams.generic.storage import Storage
from diagrams.generic.compute import Rack

# Create the diagram
with Diagram("Campaign Performance Assistant - Document Ingestion Pipeline", 
             show=False, 
             filename="document_ingestion_pipeline",
             direction="LR"):
    
    # Document Sources
    with Cluster("Document Sources"):
        pdf_files = Storage("PDF Files")
        html_files = Storage("HTML Files")
        docx_files = Storage("DOCX Files")
    
    # File Monitoring
    with Cluster("File Monitoring"):
        watchdog = Python("Watchdog")
        file_monitor = Rack("File Monitor")
    
    # Document Processing
    with Cluster("Document Processing"):
        loaders = Python("Document Loaders")
        chunking = Python("Text Chunking")
        deduplication = Python("Deduplication")
    
    # Embedding & Storage
    with Cluster("Embedding & Storage"):
        embeddings = Python("HuggingFace Embeddings")
        chroma = Storage("ChromaDB")
        processed_files = Storage("Processed Files CSV")
    
    # Logging
    with Cluster("Logging"):
        loguru = Python("Loguru")
        grafana = Python("Grafana Loki")
    
    # File Movement
    with Cluster("File Management"):
        done_folder = Storage("Done Folder")
        landing_folder = Storage("Landing Folder")
    
    # Flow
    pdf_files >> landing_folder
    html_files >> landing_folder
    docx_files >> landing_folder
    
    landing_folder >> watchdog
    watchdog >> file_monitor
    file_monitor >> loaders
    
    loaders >> chunking
    chunking >> deduplication
    deduplication >> embeddings
    
    embeddings >> chroma
    deduplication >> processed_files
    
    # Logging
    loaders >> loguru
    chunking >> loguru
    deduplication >> loguru
    embeddings >> loguru
    loguru >> grafana
    
    # File Movement
    loaders >> done_folder 