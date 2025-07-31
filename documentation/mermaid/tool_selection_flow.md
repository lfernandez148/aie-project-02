# Campaign Performance Assistant - Tool Selection Flow

```mermaid
flowchart TB
    %% User Input
    USER[User Query]
    
    %% LLM Processing
    subgraph "LLM Processing"
        LANGCHAIN[LangChain]
        LLM[OpenAI/LM Studio]
    end
    
    %% Tool Selection
    subgraph "Tool Selection"
        SELECTOR[Tool Selection]
    end
    
    %% Available Tools
    subgraph "Available Tools"
        SEARCH[search_campaign_documents]
        GET_CAMPAIGN[get_campaign_by_id]
        GET_TOP[get_top_campaigns_by_metric]
        GET_TOPIC[get_campaigns_by_topic]
        GET_SEGMENT[get_campaigns_by_segment]
        GET_STATS[get_campaign_summary_stats]
        COMPARE[compare_campaigns_by_id]
        CREATE_CHART[create_campaign_chart]
    end
    
    %% Data Sources
    subgraph "Data Sources"
        FASTAPI[FastAPI]
        CHROMA[ChromaDB]
        SQLITE[SQLite DB]
    end
    
    %% Response Types
    subgraph "Response Types"
        TEXT[Text Response]
        TABLE[Table Response]
        CHART[Chart Response]
        ERROR[Error Response]
    end
    
    %% Flow
    USER --> LANGCHAIN
    LANGCHAIN --> LLM
    LLM --> SELECTOR
    
    %% Tool Selection Paths
    SELECTOR --> SEARCH
    SELECTOR --> GET_CAMPAIGN
    SELECTOR --> GET_TOP
    SELECTOR --> GET_TOPIC
    SELECTOR --> GET_SEGMENT
    SELECTOR --> GET_STATS
    SELECTOR --> COMPARE
    SELECTOR --> CREATE_CHART
    
    %% Tool to Data Source
    SEARCH --> CHROMA
    GET_CAMPAIGN --> FASTAPI
    GET_TOP --> FASTAPI
    GET_TOPIC --> FASTAPI
    GET_SEGMENT --> FASTAPI
    GET_STATS --> FASTAPI
    COMPARE --> FASTAPI
    CREATE_CHART --> FASTAPI
    
    FASTAPI --> SQLITE
    
    %% Response Flow
    SEARCH --> TEXT
    GET_CAMPAIGN --> TEXT
    GET_TOPIC --> TEXT
    GET_SEGMENT --> TEXT
    GET_STATS --> TEXT
    COMPARE --> TEXT
    
    GET_TOP --> TABLE
    CREATE_CHART --> CHART
    
    %% Error handling
    SEARCH --> ERROR
    GET_CAMPAIGN --> ERROR
    GET_TOP --> ERROR
    GET_TOPIC --> ERROR
    GET_SEGMENT --> ERROR
    GET_STATS --> ERROR
    COMPARE --> ERROR
    CREATE_CHART --> ERROR
    
    %% Styling
    classDef user fill:#ffebee
    classDef processing fill:#f3e5f5
    classDef tools fill:#e8f5e8
    classDef data fill:#e1f5fe
    classDef response fill:#fff3e0
    
    class USER user
    class LANGCHAIN,LLM,SELECTOR processing
    class SEARCH,GET_CAMPAIGN,GET_TOP,GET_TOPIC,GET_SEGMENT,GET_STATS,COMPARE,CREATE_CHART tools
    class FASTAPI,CHROMA,SQLITE data
    class TEXT,TABLE,CHART,ERROR response
```

## Description

This diagram shows how the LLM selects and uses different tools based on user queries:

### **Available Tools**

| Tool | Purpose | Data Source |
|------|---------|-------------|
| `search_campaign_documents` | Document content search | ChromaDB |
| `get_campaign_by_id` | Specific campaign data | FastAPI |
| `get_top_campaigns_by_metric` | Top performers | FastAPI |
| `get_campaigns_by_topic` | Topic-based filtering | FastAPI |
| `get_campaigns_by_segment` | Segment-based filtering | FastAPI |
| `get_campaign_summary_stats` | Overall statistics | FastAPI |
| `compare_campaigns_by_id` | Campaign comparison | FastAPI |
| `create_campaign_chart` | Chart generation | FastAPI |

### **Tool Selection Logic**

The LLM analyzes user queries and selects the most appropriate tool based on:

- **Keywords** in the query
- **Intent** (search, compare, analyze)
- **Data type** needed (structured vs. document content)
- **Response format** required (text, table, chart)

### **Response Types**

- **Text Responses**: Natural language explanations
- **Table Responses**: Structured data in tabular format
- **Chart Responses**: Interactive visualizations
- **Error Responses**: Clear error messages with guidance 