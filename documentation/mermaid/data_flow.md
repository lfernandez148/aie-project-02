# Campaign Performance Assistant - Data Flow

```mermaid
flowchart LR
    %% User Input
    USER[User Query]
    
    %% Frontend
    subgraph "Frontend"
        STREAMLIT[Streamlit UI]
    end
    
    %% Processing Layer
    subgraph "Processing Layer"
        LANGCHAIN[LangChain]
        LLM[OpenAI/LM Studio]
        TOOLS[LLM Tools]
    end
    
    %% Data Sources
    subgraph "Data Sources"
        FASTAPI[FastAPI]
        CHROMA[ChromaDB]
        SQLITE[SQLite DB]
        DOCS[Documents]
    end
    
    %% Services
    subgraph "Services"
        AUTH[Auth]
        RATE[Rate Limiting]
        LOGGING[Logging]
    end
    
    %% External
    subgraph "External"
        GRAFANA[Grafana Loki]
        LANGSMITH[LangSmith]
    end
    
    %% Data Flow
    USER --> STREAMLIT
    STREAMLIT --> LANGCHAIN
    LANGCHAIN --> LLM
    LANGCHAIN --> TOOLS
    
    TOOLS --> FASTAPI
    TOOLS --> CHROMA
    
    FASTAPI --> AUTH
    AUTH --> RATE
    RATE --> SQLITE
    
    DOCS --> CHROMA
    
    LANGCHAIN --> LOGGING
    LOGGING --> GRAFANA
    LANGCHAIN --> LANGSMITH
    
    %% Response Flow
    LLM --> STREAMLIT
    TOOLS --> STREAMLIT
    FASTAPI --> STREAMLIT
    CHROMA --> STREAMLIT
    
    %% Styling
    classDef user fill:#ffebee
    classDef frontend fill:#e1f5fe
    classDef processing fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef services fill:#fff3e0
    classDef external fill:#fce4ec
    
    class USER user
    class STREAMLIT frontend
    class LANGCHAIN,LLM,TOOLS processing
    class FASTAPI,CHROMA,SQLITE,DOCS data
    class AUTH,RATE,LOGGING services
    class GRAFANA,LANGSMITH external
```

## Description

This diagram illustrates how data flows through the Campaign Performance Assistant system:

### **Process Flow**

1. **User Query** → Streamlit UI
2. **Streamlit** → LangChain (AI orchestration)
3. **LangChain** → LLM (OpenAI/LM Studio)
4. **LLM** → Tool Selection
5. **Tools** → Data Sources (FastAPI/ChromaDB)
6. **Data Sources** → Response Generation
7. **Response** → UI Display with Source Attribution

### **Data Sources**

- **FastAPI**: Structured campaign metrics
- **ChromaDB**: Document content search
- **SQLite**: Campaign database queries

### **Key Features**

- **Bidirectional flow**: Data flows both ways for queries and responses
- **Multiple data sources**: Combines structured and unstructured data
- **Service integration**: Authentication, logging, and monitoring
- **External services**: Grafana Loki for logging, LangSmith for monitoring 