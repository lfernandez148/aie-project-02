# TODO & Notes

## 🚀 High Priority

- [ ] UI - Response as HMTL/Markdown
- [ ] Memory
- [X] Tool matching
- [X] Function Calling / Tools
- [X] Chat history
- [X] Query database (SQL)
- [ ] Structural retriever (what is it?)
- [X] API endpoints for external integrations
- [X] API key validation
- [X] API limit rate
- [ ] Add LangSmith

## 🔧 Medium Priority

- [X] Local LLM
- [ ] Implement MCP (Client and Servier)

## 📝 Low Priority

- [ ] Charts
- [ ] User authentication
- [ ] Session management
- [ ] Unit tests
- [ ] Integration tests

## 💡 Ideas & Research

- [ ] Look into caching strategies for faster responses
- [ ] Consider using FastAPI for API endpoints
- [ ] Research vector database alternatives (Pinecone, Weaviate)
- [ ] Explort different splitting/chuncking options

## 📋 Notes

### Architecture Decisions

- Using HuggingFace embeddings for local processing
- ChromaDB for vector storage (good for development)
- Loguru for consistent logging across components

### Performance Considerations

- Document chunking size: 1000 characters
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Retrieval: Top 4 most similar documents

### Known Issues

- Large PDF files may take time to process
- Need to handle concurrent file uploads better

## ✅ Completed

- [X] Basic RAG chatbot with OpenAI
- [X] Document ingestion for PDF, HTML, DOCX
- [X] File deduplication with content hashing
- [X] Background file watcher service
- [X] Comprehensive logging with loguru
- [X] Streamlit web interface
- [X] Debug and cleanup tools
- [X] ChromaDB integration



-- AI Engineering - Project 2

## Task Requirements

**Core Requirements:**

1. **RAG Implementation:**
   * x Create a knowledge base relevant to your domain
   * x Implement standard document retrieval with embeddings
   * x Use chunking strategies and similarity search
2. **Function Calling:**
   * Implement at least 3 different function calls
   * x Functions should be relevant to your domain
   * Examples: x data analysis, calculations, x API integrations
3. **Domain Specialization:**
   * x Choose a specific domain or use case
   * x Create a focused knowledge base
   * x Implement domain-specific prompts and responses
   * Add relevant security measures for your domain
4. **Technical Implementation:**
   * x Use LangChain for OpenAI API integration
   * x Implement proper error handling
   * x Add logging and monitoring
   * Include user input validation
   * x Implement rate limiting and API key management
5. **User Interface:**
   * x Create an intuitive interface using Streamlit or Next.js
   * Show relevant context and sources
   * Display function call results
   * x Include progress indicators for long operations

---

*Last updated: [Current Date]*
