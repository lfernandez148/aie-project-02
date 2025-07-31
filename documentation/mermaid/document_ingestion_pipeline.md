# Campaign Performance Assistant - Document Ingestion Pipeline

```mermaid
flowchart LR
    %% Document Sources
    subgraph "Document Sources"
        PDF[PDF Files]
        HTML[HTML Files]
        DOCX[DOCX Files]
    end
    
    %% File Monitoring
    subgraph "File Monitoring"
        WATCHDOG[Watchdog]
        MONITOR[File Monitor]
    end
    
    %% Document Processing
    subgraph "Document Processing"
        LOADERS[Document Loaders]
        CHUNKING[Text Chunking]
        DEDUP[Deduplication]
    end
    
    %% Embedding & Storage
    subgraph "Embedding & Storage"
        EMBEDDINGS[HuggingFace Embeddings]
        CHROMA[ChromaDB]
        PROCESSED[Processed Files CSV]
    end
    
    %% Logging
    subgraph "Logging"
        LOGURU[Loguru]
        GRAFANA[Grafana Loki]
    end
    
    %% File Movement
    subgraph "File Management"
        DONE[Done Folder]
        LANDING[Landing Folder]
    end
    
    %% Flow
    PDF --> LANDING
    HTML --> LANDING
    DOCX --> LANDING
    
    LANDING --> WATCHDOG
    WATCHDOG --> MONITOR
    MONITOR --> LOADERS
    
    LOADERS --> CHUNKING
    CHUNKING --> DEDUP
    DEDUP --> EMBEDDINGS
    
    EMBEDDINGS --> CHROMA
    DEDUP --> PROCESSED
    
    %% Logging
    LOADERS --> LOGURU
    CHUNKING --> LOGURU
    DEDUP --> LOGURU
    EMBEDDINGS --> LOGURU
    LOGURU --> GRAFANA
    
    %% File Movement
    LOADERS --> DONE
    
    %% Styling
    classDef sources fill:#ffebee
    classDef monitoring fill:#e1f5fe
    classDef processing fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef logging fill:#fff3e0
    classDef management fill:#fce4ec
    
    class PDF,HTML,DOCX sources
    class WATCHDOG,MONITOR monitoring
    class LOADERS,CHUNKING,DEDUP processing
    class EMBEDDINGS,CHROMA,PROCESSED storage
    class LOGURU,GRAFANA logging
    class DONE,LANDING management
```

## Description

This diagram shows the complete document ingestion pipeline from file upload to vector database storage:

### **Processing Steps**

1. **File Upload**: PDF, HTML, DOCX files placed in landing folder
2. **File Monitoring**: Watchdog detects new files
3. **Document Loading**: Appropriate loader extracts text
4. **Text Chunking**: Documents split into 1000-character chunks
5. **Deduplication**: MD5 hash-based duplicate detection
6. **Embedding Generation**: HuggingFace embeddings created
7. **Vector Storage**: Embeddings stored in ChromaDB
8. **File Movement**: Processed files moved to done folder
9. **Logging**: All steps logged to Grafana Loki

### **Supported Formats**

- **PDF**: PyPDFLoader
- **HTML**: UnstructuredHTMLLoader  
- **DOCX**: UnstructuredWordDocumentLoader

### **Key Features**

- **Automatic processing**: Background service monitors for new files
- **Deduplication**: Prevents duplicate document processing
- **Chunking**: Optimizes for vector search performance
- **Comprehensive logging**: All steps tracked for debugging
- **File management**: Organized folder structure 