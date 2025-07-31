# Campaign Performance Assistant - Complete Documentation

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Data Flow](#data-flow)
4. [Tool Selection Process](#tool-selection-process)
5. [Document Ingestion Pipeline](#document-ingestion-pipeline)
6. [API Reference](#api-reference)
7. [Installation & Setup](#installation--setup)
8. [Usage Guide](#usage-guide)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

The **Campaign Performance Assistant** is an AI-powered chatbot system that provides intelligent insights into campaign data. It combines:

- **Natural Language Processing** with OpenAI/LM Studio
- **Retrieval Augmented Generation (RAG)** for document search
- **Structured data queries** via FastAPI
- **Interactive visualizations** with charts and tables
- **Real-time document ingestion** with automatic processing

### Key Features

✅ **Multi-format document support** (PDF, HTML, DOCX)  
✅ **Intelligent tool selection** based on user queries  
✅ **Source attribution** for all responses  
✅ **Real-time chart generation**  
✅ **Structured data tables**  
✅ **Background document processing**  
✅ **Comprehensive logging** with Grafana Loki  
✅ **API authentication** and rate limiting  

---

## 🏗️ Architecture

![System Architecture](diagrams/system_architecture.png)

### Core Components

#### **Frontend Layer**
- **Streamlit UI**: Web-based chat interface
- **Mobile Access**: Responsive design for mobile devices
- **Web Browser**: Standard web access

#### **Backend Layer**
- **FastAPI**: REST API for structured data access
- **LangChain**: AI orchestration and tool management
- **OpenAI/LM Studio**: Large Language Model processing

#### **Data Layer**
- **SQLite DB**: Structured campaign data storage
- **ChromaDB**: Vector database for document embeddings
- **Documents**: Multi-format document storage

#### **Services Layer**
- **Authentication**: API key-based security
- **Rate Limiting**: Request throttling
- **Logging**: Loguru + Grafana Loki integration

#### **External Services**
- **Grafana Loki**: Log aggregation and visualization
- **LangSmith**: LLM monitoring and debugging

---

## 🔄 Data Flow

![Data Flow](diagrams/data_flow.png)

### Process Flow

1. **User Query** → Streamlit UI
2. **Streamlit** → LangChain (AI orchestration)
3. **LangChain** → LLM (OpenAI/LM Studio)
4. **LLM** → Tool Selection
5. **Tools** → Data Sources (FastAPI/ChromaDB)
6. **Data Sources** → Response Generation
7. **Response** → UI Display with Source Attribution

### Data Sources

- **FastAPI**: Structured campaign metrics
- **ChromaDB**: Document content search
- **SQLite**: Campaign database queries

---

## 🛠️ Tool Selection Process

![Tool Selection Flow](diagrams/tool_selection_flow.png)

### Available Tools

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

### Tool Selection Logic

The LLM analyzes user queries and selects the most appropriate tool based on:

- **Keywords** in the query
- **Intent** (search, compare, analyze)
- **Data type** needed (structured vs. document content)
- **Response format** required (text, table, chart)

---

## 📄 Document Ingestion Pipeline

![Document Ingestion Pipeline](diagrams/document_ingestion_pipeline.png)

### Processing Steps

1. **File Upload**: PDF, HTML, DOCX files placed in landing folder
2. **File Monitoring**: Watchdog detects new files
3. **Document Loading**: Appropriate loader extracts text
4. **Text Chunking**: Documents split into 1000-character chunks
5. **Deduplication**: MD5 hash-based duplicate detection
6. **Embedding Generation**: HuggingFace embeddings created
7. **Vector Storage**: Embeddings stored in ChromaDB
8. **File Movement**: Processed files moved to done folder
9. **Logging**: All steps logged to Grafana Loki

### Supported Formats

- **PDF**: PyPDFLoader
- **HTML**: UnstructuredHTMLLoader  
- **DOCX**: UnstructuredWordDocumentLoader

---

## 🔌 API Reference

![API Endpoints](diagrams/api_endpoints.png)

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root health check |
| `/health` | GET | Detailed health status |

### Campaign Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/campaigns/{id}` | GET | Get campaign by ID | `id: int` |
| `/campaigns/top/{metric}` | GET | Top campaigns by metric | `metric: str, limit: int` |
| `/campaigns/summary` | GET | Summary statistics | None |
| `/campaigns/topic/{topic}` | GET | Campaigns by topic | `topic: str` |
| `/campaigns/segment/{segment}` | GET | Campaigns by segment | `segment: str` |
| `/campaigns/compare/{id1}/{id2}` | GET | Compare two campaigns | `id1: int, id2: int` |
| `/campaigns/all` | GET | Get all campaigns | None |

### Documentation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/docs` | GET | Swagger UI documentation |
| `/redoc` | GET | ReDoc documentation |

### Authentication

All endpoints require API key authentication:
```
Authorization: Bearer sk-test-1234567890abcdef
```

### Rate Limiting

- **Default**: 100 requests per minute per API key
- **Configurable**: Via environment variables

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.7+
- UV package manager
- Graphviz (for diagrams)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project-02
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Install Graphviz** (for diagrams)
   ```bash
   brew install graphviz  # macOS
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Initialize database**
   ```bash
   python database/database_setup.py
   ```

6. **Start document ingestion service**
   ```bash
   cd docs_loader
   python ingest.py
   ```

7. **Start FastAPI server**
   ```bash
   cd api
   uvicorn main:app --reload
   ```

8. **Start Streamlit application**
   ```bash
   streamlit run main.py
   ```

---

## 📖 Usage Guide

### Starting the System

1. **Start all services**:
   ```bash
   # Terminal 1: Document ingestion
   cd docs_loader && python ingest.py
   
   # Terminal 2: FastAPI server
   cd api && uvicorn main:app --reload
   
   # Terminal 3: Streamlit app
   streamlit run main.py
   ```

2. **Access the application**:
   - **Streamlit UI**: http://localhost:8501
   - **FastAPI Docs**: http://localhost:8000/docs
   - **Grafana Loki**: http://localhost:3100

### Sample Queries

#### **Document Search**
- "What does the executive summary say about campaign 101?"
- "Show me performance insights from the reports"
- "What recommendations are in the campaign documents?"

#### **Structured Data**
- "What are the metrics for campaign 102?"
- "Show me the top 5 campaigns by conversion rate"
- "Compare campaigns 101 and 102"
- "Get summary statistics for all campaigns"

#### **Visualizations**
- "Create a bar chart of audience volume by topic"
- "Show me a table of top campaigns by opens"

#### **Filtering**
- "Show campaigns about loyalty programs"
- "List campaigns for the retail segment"

### Response Types

1. **Text Responses**: Natural language explanations
2. **Table Responses**: Structured data in tabular format
3. **Chart Responses**: Interactive visualizations
4. **Error Responses**: Clear error messages with guidance

### Source Attribution

All responses include source information:
- **Vector Database**: Document name and type
- **Campaign Database**: Database table reference
- **Chart Generation**: Tool and data source

---

## 🔧 Troubleshooting

### Common Issues

#### **Document Ingestion Problems**
- **Issue**: Documents not being processed
- **Solution**: Check `docs_loader/logs/` for errors
- **Check**: Ensure files are in `docs_loader/docs/landing/`

#### **Vector Search Issues**
- **Issue**: High similarity scores (>1.2)
- **Solution**: Re-run document ingestion with chunking
- **Debug**: Use `docs_loader/debug_vector_search.py`

#### **API Connection Errors**
- **Issue**: FastAPI not responding
- **Solution**: Check if server is running on port 8000
- **Verify**: Test with `curl http://localhost:8000/health`

#### **LLM Tool Selection**
- **Issue**: Wrong tool being selected
- **Solution**: Check tool descriptions in `llm_tools.py`
- **Improve**: Add more specific examples to tool descriptions

### Debug Tools

1. **Vector Search Debug**:
   ```bash
   cd docs_loader
   python debug_vector_search.py
   ```

2. **API Testing**:
   ```bash
   cd api
   python test_api.py
   ```

3. **Memory Testing**:
   ```bash
   python utils/test_memory.py
   ```

4. **Chart Testing**:
   ```bash
   python utils/test_charts.py
   ```

### Log Files

- **Application Logs**: `logs/chatbot.log`
- **Ingestion Logs**: `docs_loader/logs/ingest.log`
- **API Logs**: `api/logs/api.log`
- **Debug Logs**: `docs_loader/logs/debug_vector.log`

### Performance Optimization

1. **Vector Search**: Adjust similarity threshold in `llm_tools.py`
2. **Chunking**: Modify chunk size in `docs_loader/ingest.py`
3. **Rate Limiting**: Configure limits in `api/main.py`
4. **Memory**: Monitor conversation buffer size

---

## 📊 Monitoring & Observability

### Logging Strategy

- **Loguru**: Structured logging with rotation
- **Grafana Loki**: Centralized log aggregation
- **LangSmith**: LLM performance monitoring

### Key Metrics

- **Response Time**: Tool execution and LLM processing
- **Tool Usage**: Frequency of each tool
- **Error Rates**: API and LLM error tracking
- **Document Processing**: Ingestion success rates

### Health Checks

- **API Health**: `/health` endpoint
- **Database**: SQLite connection status
- **Vector DB**: ChromaDB availability
- **LLM**: OpenAI/LM Studio connectivity

---

## 🔮 Future Enhancements

### Planned Features

1. **Additional Document Formats**: Excel, PowerPoint
2. **Advanced Analytics**: Trend analysis, forecasting
3. **User Management**: Multi-user support
4. **Export Capabilities**: PDF reports, data export
5. **Mobile App**: Native mobile application
6. **Real-time Updates**: WebSocket notifications

### Technical Improvements

1. **Caching**: Redis for response caching
2. **Load Balancing**: Multiple API instances
3. **Database Migration**: PostgreSQL for production
4. **Containerization**: Docker deployment
5. **CI/CD**: Automated testing and deployment

---

## 📝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** and test thoroughly
4. **Update documentation** and diagrams
5. **Submit pull request** with detailed description

### Code Standards

- **Python**: PEP 8 style guide
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests for new features
- **Diagrams**: Update when architecture changes

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Support

For support and questions:

- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check this file and inline comments
- **Testing**: Use the provided test scripts

---

*Last updated: July 31, 2024* 