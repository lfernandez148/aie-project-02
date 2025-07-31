# Campaign Performance Assistant - System Architecture

```mermaid
graph TB
    %% User Interface Layer
    subgraph "Frontend Layer"
        UI[Streamlit UI]
        MOBILE[Mobile Access]
        BROWSER[Web Browser]
    end
    
    %% Backend Layer
    subgraph "Backend Layer"
        FASTAPI[FastAPI]
        LANGCHAIN[LangChain]
        LLM[OpenAI/LM Studio]
    end
    
    %% Data Layer
    subgraph "Data Layer"
        SQLITE[SQLite DB]
        CHROMA[ChromaDB]
        DOCS[Documents]
    end
    
    %% Services Layer
    subgraph "Services Layer"
        AUTH[Authentication]
        RATE[Rate Limiting]
        LOGGING[Loguru + Loki]
    end
    
    %% External Services
    subgraph "External Services"
        GRAFANA[Grafana Loki]
        LANGSMITH[LangSmith]
    end
    
    %% Connections
    UI --> FASTAPI
    MOBILE --> FASTAPI
    BROWSER --> FASTAPI
    
    FASTAPI --> AUTH
    AUTH --> RATE
    RATE --> SQLITE
    
    LANGCHAIN --> LLM
    LANGCHAIN --> CHROMA
    LANGCHAIN --> FASTAPI
    
    DOCS --> CHROMA
    
    LOGGING --> GRAFANA
    LANGCHAIN --> LANGSMITH
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef services fill:#fff3e0
    classDef external fill:#fce4ec
    
    class UI,MOBILE,BROWSER frontend
    class FASTAPI,LANGCHAIN,LLM backend
    class SQLITE,CHROMA,DOCS data
    class AUTH,RATE,LOGGING services
    class GRAFANA,LANGSMITH external
```

## Description

This diagram shows the complete system architecture of the Campaign Performance Assistant:

### **Frontend Layer**
- **Streamlit UI**: Web-based chat interface
- **Mobile Access**: Responsive design for mobile devices  
- **Web Browser**: Standard web access

### **Backend Layer**
- **FastAPI**: REST API for structured data access
- **LangChain**: AI orchestration and tool management
- **OpenAI/LM Studio**: Large Language Model processing

### **Data Layer**
- **SQLite DB**: Structured campaign data storage
- **ChromaDB**: Vector database for document embeddings
- **Documents**: Multi-format document storage

### **Services Layer**
- **Authentication**: API key-based security
- **Rate Limiting**: Request throttling
- **Logging**: Loguru + Grafana Loki integration

### **External Services**
- **Grafana Loki**: Log aggregation and visualization
- **LangSmith**: LLM monitoring and debugging 