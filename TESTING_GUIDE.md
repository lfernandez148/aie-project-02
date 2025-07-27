# Campaign Performance Assistant - Testing & Troubleshooting Guide

## 📋 Table of Contents
- [Testing Scenarios](#testing-scenarios)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Debugging Commands](#debugging-commands)
- [Performance Testing](#performance-testing)
- [Expected Results](#expected-results)
- [Testing Checklist](#testing-checklist)

---

## 🧪 Testing Scenarios

### 📊 Database Query Tests

#### 1. Basic Campaign Queries
```bash
# Test individual campaign details
"What's the ROI for campaign 100?"
"Get details for campaign 101"
"Show me campaign 200 information"
```

#### 2. Analytics & Metrics
```bash
# Test summary statistics
"Get summary statistics for all campaigns"
"What are the overall campaign performance metrics?"

# Test top performers
"Get top 3 campaigns by conversion rate"
"Show me top 5 campaigns by open rate"
"Which campaigns have the highest click rates?"
```

#### 3. Comparisons
```bash
# Test campaign comparisons
"Compare campaigns 100 and 101"
"Compare the performance of campaign 200 vs 201"
"Which campaign performed better: 100 or 101?"
```

#### 4. Topic & Segment Analysis
```bash
# Test topic-based queries
"Get campaigns for topic 'Holiday Sales Event'"
"Show me all fitness gear promotions"
"Find campaigns about summer sales"

# Test segment-based queries
"Get campaigns for segment 'Premium Customers'"
"Show campaigns targeting 'New Users'"
```

### 📄 Document Search Tests

#### 1. RAG Functionality
```bash
# Test document search
"Search for information about summer campaigns"
"Find holiday campaign reports"
"Look for fitness gear promotion documents"
"Search for documents about email marketing strategies"
```

#### 2. Combined Queries
```bash
# Test mixed queries
"What's the performance of campaign 100 and show me related documents?"
"Compare campaigns and find supporting documentation"
"Get summary stats and search for detailed reports"
```

### ⚠️ Edge Cases & Error Handling

#### 1. Non-existent Data
```bash
# Test error handling
"Get details for campaign 999"  # Should handle gracefully
"Compare campaigns 999 and 998"  # Should handle gracefully
"Search for non-existent topic"  # Should return appropriate message
```

#### 2. Ambiguous Queries
```bash
# Test ambiguous requests
"What's the best campaign?"  # Should ask for clarification
"Show me everything"  # Should provide guidance
"Compare campaigns"  # Should ask for specific campaigns
```

---

## 🔧 Troubleshooting Guide

### 🚨 Common Issues & Solutions

#### 1. Database Connection Errors
```bash
# Error: "unable to open database file"
Solution: Run database setup
cd database
python database_setup.py
```

#### 2. Tool Not Called
```bash
# Check logs for tool execution
tail -f logs/chatbot.log

# Verify tool names match
python -c "from llm_tools import LLM_TOOLS; [print(tool.name) for tool in LLM_TOOLS]"
```

#### 3. RAG Not Working
```bash
# Check if documents are ingested
ls -la chroma_db/

# Re-run ingestion if needed
cd docs_loader
python ingest.py
```

#### 4. LLM Connection Issues
```bash
# Check environment variables
cat .env

# Test LLM connection
python -c "from chatbot import llm; print(llm.invoke('Hello'))"
```

#### 5. Missing Dependencies
```bash
# Install missing packages
uv pip install -r requirements.txt

# Check installed packages
uv pip list | grep langchain
```

### 🔍 Debugging Commands

#### 1. Check System Status
```bash
# Check all components
echo "=== Database ==="
ls -la database/sqlite_db/
echo "=== ChromaDB ==="
ls -la chroma_db/
echo "=== Logs ==="
ls -la logs/
echo "=== Environment ==="
cat .env
```

#### 2. Test Individual Components
```bash
# Test database
cd database
python database_setup.py

# Test tools
python -c "from llm_tools import get_campaign_summary_stats; print(get_campaign_summary_stats())"

# Test RAG
python -c "from llm_tools import search_campaign_documents; print(search_campaign_documents('summer'))"
```

#### 3. Monitor Logs
```bash
# Real-time log monitoring
tail -f logs/chatbot.log

# Check for errors
grep -i error logs/chatbot.log
grep -i warning logs/chatbot.log

# Check tool execution
grep -i "executing tool" logs/chatbot.log
```

#### 4. Database Query Debugging
```python
# Test database queries directly
from database.database_setup import get_database_connection
conn = get_database_connection()
result = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()
print(f"Total campaigns: {result[0]}")
```

#### 5. Tool Execution Debugging
```python
# Add this to chatbot.py for detailed debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or check tool execution step by step
def debug_tool_execution(user_query):
    print(f"Query: {user_query}")
    print(f"Available tools: {[tool.name for tool in LLM_TOOLS]}")
    # ... rest of debugging code
```

---

## ⚡ Performance Testing

### 1. Response Time Tests
```bash
# Test simple queries
time python -c "from chatbot import chat_query; print(chat_query('Get summary statistics'))"

# Test complex queries
time python -c "from chatbot import chat_query; print(chat_query('Compare campaigns 100 and 101 and search for related documents'))"
```

### 2. Load Testing
```bash
# Test multiple queries
for i in {1..5}; do
  echo "Query $i:"
  python -c "from chatbot import chat_query; print(chat_query('Get summary statistics'))"
  echo "---"
done
```

### 3. Memory Usage
```bash
# Monitor memory usage during testing
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

---

## 📊 Expected Results

### ✅ Successful Responses Should:
- **Database queries**: Return formatted campaign data
- **RAG queries**: Return relevant document excerpts
- **Combined queries**: Synthesize information from multiple sources
- **Error cases**: Provide helpful error messages

### ❌ Failed Responses Should:
- **Log detailed errors** in `logs/chatbot.log`
- **Provide fallback responses** when tools fail
- **Give clear error messages** to users

### 📋 Sample Expected Outputs

#### Database Query Response:
```
Campaign Summary Statistics:
- Total Campaigns: 1,000
- Average Conversion Rate: 2.45%
- Average Open Rate: 25.67%
- Average Click Rate: 3.89%
- Total Conversions: 24,500
- Total Opens: 256,700
- Total Clicks: 38,900
```

#### RAG Query Response:
```
Found relevant campaign information:

Campaign Performance Report - Summer 2024
The summer campaign achieved a 15% increase in conversion rates...
[Additional document content]
```

#### Combined Query Response:
```
Based on the database analysis and document search:

Campaign 100 Performance:
- Conversion Rate: 3.2%
- Revenue: $15,000

Related Documents:
Summer campaign analysis shows strong performance...
[Combined insights from both sources]
```

---

## 🎯 Testing Checklist

### Core Functionality
- [ ] **Database queries work**
- [ ] **RAG document search works**
- [ ] **Tool calling is working**
- [ ] **Error handling is graceful**
- [ ] **UI is responsive**
- [ ] **Logs are informative**
- [ ] **Performance is acceptable**

### Specific Features
- [ ] **Campaign details by ID**
- [ ] **Top performers by metric**
- [ ] **Campaign comparisons**
- [ ] **Summary statistics**
- [ ] **Topic-based searches**
- [ ] **Segment analysis**
- [ ] **Document search**
- [ ] **Combined queries**

### Error Handling
- [ ] **Non-existent campaigns**
- [ ] **Invalid queries**
- [ ] **Database connection issues**
- [ ] **LLM connection issues**
- [ ] **Tool execution failures**

### Performance
- [ ] **Response time < 5 seconds**
- [ ] **Memory usage stable**
- [ ] **Concurrent queries work**
- [ ] **Large result sets handled**

---

## 🚀 Quick Start Testing

### 1. Basic Functionality Test
```bash
# Start the application
streamlit run main.py

# Test basic query
curl -X POST "http://localhost:8501" -d "Get summary statistics for all campaigns"
```

### 2. Comprehensive Test Suite
```bash
# Run all test scenarios
python -c "
from chatbot import chat_query
test_queries = [
    'Get summary statistics for all campaigns',
    'What is the ROI for campaign 100?',
    'Compare campaigns 100 and 101',
    'Search for information about summer campaigns',
    'Get top 3 campaigns by conversion rate'
]
for query in test_queries:
    print(f'Testing: {query}')
    try:
        response = chat_query(query)
        print(f'Response: {response[:200]}...')
    except Exception as e:
        print(f'Error: {e}')
    print('---')
"
```

### 3. Log Analysis
```bash
# Analyze logs for issues
echo "=== Error Summary ==="
grep -i error logs/chatbot.log | wc -l
echo "=== Warning Summary ==="
grep -i warning logs/chatbot.log | wc -l
echo "=== Tool Execution Summary ==="
grep -i "executing tool" logs/chatbot.log | wc -l
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- [ ] **Monitor log files** for errors
- [ ] **Check database size** and performance
- [ ] **Update dependencies** regularly
- [ ] **Backup database** and ChromaDB
- [ ] **Test after updates** to ensure functionality

### Performance Monitoring
- [ ] **Response time tracking**
- [ ] **Memory usage monitoring**
- [ ] **Error rate tracking**
- [ ] **User query analysis**

### Troubleshooting Workflow
1. **Check logs** for error messages
2. **Verify dependencies** are installed
3. **Test individual components**
4. **Check configuration** files
5. **Restart services** if needed
6. **Contact support** if issues persist

---

*Last updated: $(date)*
*Version: 1.0* 