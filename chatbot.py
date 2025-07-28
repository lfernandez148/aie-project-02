# chatbot.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from loguru import logger
from dotenv import load_dotenv
from llm_tools import LLM_TOOLS
import os

load_dotenv()

CHROMA_DIR = "chroma_db"
LOGS_FOLDER = "logs"

# Configuration: Choose between OpenAI and LM Studio
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LM_STUDIO_URL = "http://localhost:1234"

logger.add(
    f"{LOGS_FOLDER}/chatbot.log", 
    rotation="1 week", 
    retention="4 weeks", 
    level="INFO"
)

# Load the persisted Chroma DB and retriever
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 4})

# Initialize LLM based on configuration
if USE_LOCAL_LLM:
    logger.info("Using local LLM via LM Studio")
    llm = ChatOpenAI(
        base_url=f"{LM_STUDIO_URL}/v1",
        api_key="not-needed",  # LM Studio doesn't require API key
        temperature=0,
        model="local-model"  # This can be any name since LM Studio ignores it
    )
else:
    logger.info("Using OpenAI")
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo"  # or any other OpenAI model
    )

# Initialize conversation memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    max_token_limit=2000  # Limit memory to prevent token overflow
)

logger.info("Memory system initialized with conversation buffer")

SAMPLE_QUESTIONS = [
    "Show me the top 5 campaigns by conversion rate",
    "What is the average open rate for all campaigns?",
    "Compare campaign 101 and campaign 102",
    "Show me a bar chart of audience volume by topic",
    "List all campaigns for the Retail segment",
    "Get summary statistics for all campaigns",
    "Show me the top campaigns by clicks",
    "What are the trends in conversion rate over time?",
    "Show me a table of top campaigns by open rate",
    "Show me the top 10 campaigns"
]

HELP_TRIGGERS = [
    "what can i ask",
    "what kind of question",
    "help",
    "examples",
    "sample questions",
    "how to use",
    "what do you do",
    "what can you do",
    "how can you help"
]


def chat_query_with_direct_tools(user_query: str, session_id: str = "default") -> str:
    """Use direct function calling with memory."""
    logger.info(f"Processing query with memory: {user_query}")
    
    # Check for help/example triggers
    if any(trigger in user_query.lower() for trigger in HELP_TRIGGERS):
        return {
            "type": "examples",
            "message": "Here are some sample questions you can ask:",
            "examples": SAMPLE_QUESTIONS
        }

    try:
        # Get conversation history from memory
        chat_history = memory.chat_memory.messages
        logger.info(f"Retrieved {len(chat_history)} messages from memory")
        
        # Use all tools from llm_tools (includes RAG and database tools)
        all_tools = LLM_TOOLS
        
        # Log available tools for debugging
        logger.info(f"Available tools: {[tool.name for tool in all_tools]}")
        
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(all_tools)
        
        # Create messages with history
        messages = []
        
        # Add system message with context about being a campaign assistant
        system_message = HumanMessage(content=(
            "You are a Campaign Performance Assistant. "
            "You ONLY answer questions about campaign data and marketing campaigns. "
            "Use the available tools to get accurate information and provide helpful insights. "
            "If no relevant campaign data is found, respond with: "
            "'I'm only able to answer questions about campaign data. "
            "Please ask something related to your campaigns.' "
            "Always be conversational and remember previous context from the conversation."
        ))
        messages.append(system_message)
        
        # Add conversation history
        messages.extend(chat_history)
        
        # Add current user query
        messages.append(HumanMessage(content=user_query))
        
        # Get response with potential tool calls
        response = llm_with_tools.invoke(messages)
        
        # Check if the LLM wants to call any tools
        if response.tool_calls:
            logger.info(f"LLM requested {len(response.tool_calls)} tool calls")
            
            # Execute each tool call
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                # Find and execute the appropriate tool
                tool_executed = False
                for available_tool in all_tools:
                    if available_tool.name == tool_name:
                        logger.info(f"Found matching tool: {available_tool.name}")
                        result = available_tool.invoke(tool_args)
                        logger.info(f"Tool result: {result}")
                        tool_results.append({
                            "tool_name": tool_name,
                            "result": result
                        })
                        tool_executed = True
                        break
                
                if not tool_executed:
                    logger.warning(f"Tool not found: {tool_name}")
                    result = f"Unknown tool: {tool_name}"
                    tool_results.append({
                        "tool_name": tool_name,
                        "result": result
                    })
            
            # PATCH: If any tool result is a chart dict, return it immediately
            for result in tool_results:
                if isinstance(result['result'], dict) and result['result'].get('type') == 'chart':
                    # Save conversation to memory
                    memory.chat_memory.add_user_message(user_query)
                    memory.chat_memory.add_ai_message(result['result'].get('message', ''))
                    logger.info("Returning chart tool result directly to UI.")
                    return result['result']
            # PATCH: If any tool result is a table dict, return it immediately
            for result in tool_results:
                if isinstance(result['result'], dict) and result['result'].get('type') == 'table':
                    memory.chat_memory.add_user_message(user_query)
                    memory.chat_memory.add_ai_message(result['result'].get('message', ''))
                    logger.info("Returning table tool result directly to UI.")
                    return result['result']
            
            # Check if any tool returned meaningful data
            meaningful_data = False
            for result in tool_results:
                if result['tool_name'] == 'search_campaign_documents':
                    # For RAG tool, check if it found documents
                    if "No relevant campaign documents found" not in result['result']:
                        meaningful_data = True
                        break
                else:
                    # For database tools, check if they returned data
                    if isinstance(result['result'], str) and "not found" not in result['result'].lower() and "error" not in result['result'].lower():
                        meaningful_data = True
                        break
            
            if meaningful_data:
                # Create a follow-up message with tool results
                tool_results_text = "\n\n".join([
                    f"Tool {result['tool_name']} result:\n{result['result']}"
                    for result in tool_results
                ])
                
                follow_up_prompt = f"""
Based on the tool results below and our conversation history, please provide a comprehensive answer to the user's question: "{user_query}"

Tool Results:
{tool_results_text}

Please synthesize this information into a clear, helpful response that takes into account our previous conversation.
                """.strip()
                
                # Get final response
                final_response = llm.invoke(follow_up_prompt)
                final_answer = final_response.content
            else:
                # No meaningful data found
                final_answer = (
                    "I couldn't find relevant campaign information for your question. "
                    "Please try rephrasing or ask about a specific campaign, metric, topic or segment!"
                )
            
        else:
            # No tool calls needed, check if we should use RAG fallback
            logger.info("No tool calls requested, checking RAG fallback")
            context = retrieve_campaign_context(user_query)
            if context:
                # Use RAG fallback since we found relevant documents
                final_answer = call_llm_with_memory(user_query, context, "")
            else:
                # No relevant data found
                final_answer = (
                    "I couldn't find relevant campaign information for your question. "
                    "Please try rephrasing or ask about a specific campaign, metric, topic or segment!"
                )
        
        # Save conversation to memory
        memory.chat_memory.add_user_message(user_query)
        memory.chat_memory.add_ai_message(final_answer)
        
        logger.info(f"Saved conversation to memory. Total messages: {len(memory.chat_memory.messages)}")
        
        return final_answer
            
    except Exception as e:
        logger.error(f"Error in direct tool calling with memory: {e}")
        # Fallback to simple RAG with memory
        return chat_query_fallback_with_memory(user_query)


def chat_query_fallback_with_memory(user_query: str) -> str:
    """Fallback to simple RAG method with memory."""
    logger.info(f"Using fallback RAG method with memory for: {user_query}")
    
    # Get conversation history
    chat_history = memory.chat_memory.messages
    
    context = retrieve_campaign_context(user_query)
    if not context:
        return (
            "I couldn't find relevant campaign information for your question. "
            "Please try rephrasing or ask about a specific campaign, metric, topic or segment!"
        )
    
    # Create prompt with memory
    history_text = ""
    if chat_history:
        history_text = "\n\nPrevious conversation:\n"
        for msg in chat_history[-4:]:  # Last 4 messages for context
            if isinstance(msg, HumanMessage):
                history_text += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history_text += f"Assistant: {msg.content}\n"
    
    response = call_llm_with_memory(user_query, context, history_text)
    
    # Save to memory
    memory.chat_memory.add_user_message(user_query)
    memory.chat_memory.add_ai_message(response)
    
    return response


def call_llm_with_memory(user_query: str, context: str, history_text: str) -> str:
    """LLM call method with memory."""
    logger.info(f"Generating response with memory for query: {user_query}")
    
    prompt = (
        f"You are a helpful Campaign Performance Assistant. "
        f"Use the campaign data and conversation history to answer the question.\n\n"
        f"{history_text}\n"
        f"Campaign Data:\n{context}\n\n"
        f"Question: {user_query}\n"
        f"Answer:"
    )
    
    response = llm.invoke(prompt)
    logger.success(f"Generated response with memory for query: {user_query}")
    return response.content.strip()


def retrieve_campaign_context(user_query: str):
    """Original RAG context retrieval with similarity threshold."""
    logger.info(f"Processing query: {user_query}")
    
    # Use similarity search with scores to filter relevant documents
    docs_and_scores = db.similarity_search_with_score(user_query, k=4)
    
    # Filter documents with similarity score above threshold (0.5 is a good threshold)
    relevant_docs = []
    for doc, score in docs_and_scores:
        logger.info(f"Document similarity score: {score:.4f}")
        if score < 0.5:  # Lower score = more similar (cosine distance)
            relevant_docs.append(doc)
    
    if not relevant_docs:
        logger.warning(f"No relevant documents found for query: {user_query}")
        return None
    
    logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
    
    # Log details about each retrieved document
    for i, doc in enumerate(relevant_docs):
        logger.info(f"Document {i+1}:")
        logger.info(f"  Content preview: {doc.page_content[:200]}...")
        if hasattr(doc, 'metadata') and doc.metadata:
            logger.info(f"  Metadata: {doc.metadata}")
        else:
            logger.info("  Metadata: None")
    
    context = "\n".join([doc.page_content for doc in relevant_docs])
    logger.debug(f"Context length: {len(context)} characters")
    logger.info(f"Full context preview: {context[:500]}...")
    return context


def call_llm(user_query: str, context: str) -> str:
    """Original LLM call method."""
    logger.info(f"Generating response for query: {user_query}")
    prompt = (
        f"Use only the following campaign data to answer the question.\n"
        f"Campaign Data:\n{context}\n\n"
        f"Question: {user_query}\n"
        f"Answer:"
    )
    response = llm.invoke(prompt)
    logger.success(f"Generated response for query: {user_query}")
    return response.content.strip()


def chat_query(user_query: str) -> str:
    """Main chat function - uses direct tools with memory."""
    return chat_query_with_direct_tools(user_query)


def clear_memory():
    """Clear the conversation memory."""
    memory.clear()
    logger.info("Conversation memory cleared")


def get_memory_stats():
    """Get statistics about the conversation memory."""
    messages = memory.chat_memory.messages
    return {
        "total_messages": len(messages),
        "user_messages": len([m for m in messages if isinstance(m, HumanMessage)]),
        "ai_messages": len([m for m in messages if isinstance(m, AIMessage)]),
        "memory_usage": "active" if messages else "empty"
    }
