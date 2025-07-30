# TODO & Notes

## 🚀 High Priority

- [X] UI - Response as HMTL/Markdown
- [X] Memory
- [X] Tool matching
- [X] Function Calling / Tools
- [X] Chat history
- [X] Query database (SQL)
- [X] API endpoints for external integrations
- [X] API key validation
- [X] API limit rate
- [ ] Add LangSmith

## 🔧 Medium Priority

- [X] Local LLM
- [ ] Implement MCP (Client and Servier)

## 📝 Low Priority

- [X] Charts
- [ ] User authentication
- [ ] Session management
- [ ] Unit tests
- [ ] Integration tests
- [X] Structural retriever (Pydantic?)

## 💡 Ideas & Research

- [ ] Look into caching strategies for faster responses
- [X] Consider using FastAPI for API endpoints
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

- Fix: VectorDB getting Campaing Executive
  - Summary and passing to LLM, score < 0.5 (for some reason not getting documents)
  - We may need to tune chunks
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

1. **x RAG Implementation:**
   * x Create a knowledge base relevant to your domain
   * x Implement standard document retrieval with embeddings
   * x Use chunking strategies and similarity search
2. **x Function Calling:**
   * x Implement at least 3 different function calls
   * x Functions should be relevant to your domain
   * x Examples: x data analysis, calculations, x API integrations, x chart
3. **x Domain Specialization:**
   * x Choose a specific domain or use case
   * x Create a focused knowledge base
   * x Implement domain-specific prompts and responses
   * x Add relevant security measures for your domain
4. **x Technical Implementation:**
   * x Use LangChain for OpenAI API integration
   * x Implement proper error handling
   * x Add logging and monitoring
   * x Include user input validation
   * x Implement rate limiting and API key management
5. **User Interface:**
   * x Create an intuitive interface using Streamlit or Next.js
   * Show relevant context and sources
   * Display function call results
   * x Include progress indicators for long operations

---

*Last updated: [Current Date]*
