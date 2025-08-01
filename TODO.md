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
- [X] Add LangSmith

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
5. **x User Interface:**

   * x Create an intuitive interface using Streamlit or Next.js
   * x Show relevant context and sources
   * x Display function call results
   * x Include progress indicators for long operations

   ## Optional Tasks

   After the main functionality is implemented and your code works correctly, and you feel that you want to upgrade your project, choose one or more improvements from this list. The list is sorted by difficulty levels.

   **Caution: Some of the tasks in medium or hard categories may contain tasks with concepts or libraries that may be introduced in later sections or even require outside knowledge/time to research outside of the course.**

   **Easy:**


   1. Add conversation history and export functionality
   2. Add visualization of RAG process
   3. **x Include source citations in responses**
   4. Add an interactive help feature or chatbot guide

   **Medium:**

   1. **x Implement multi-model support (OpenAI, Anthropic, etc.)**
   2. **x Add real-time data updates to knowledge base**
   3. Implement advanced caching strategies
   4. Add user authentication and personalization
   5. Calculate and display token usage and costs
   6. Add visualization of function call results
   7. Implement conversation export in various formats (PDF, CSV, JSON)
   8. Connect to tools from a publicly available remote MCP server

   **Hard:**

   1. Deploy to cloud with proper scaling
   2. Implement advanced indexing (e.g., RAPTOR, ColBERT)
   3. Implement A/B testing for different RAG strategies
   4. **x Add automated knowledge base updates**
   5. Fine-tune the model for your specific domain
   6. Add multi-language support
   7. Implement advanced analytics dashboard
   8. Implement your tools (functions) as MCP servers

---

*Last updated: [Current Date]*
