# chatbot.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
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


def chat_query_with_direct_tools(user_query: str) -> str:
    """Use direct function calling without agents."""
    logger.info(f"Processing query with direct tools: {user_query}")
    
    try:
        # Use all tools from llm_tools (includes RAG and database tools)
        all_tools = LLM_TOOLS
        
        # Log available tools for debugging
        logger.info(f"Available tools: {[tool.name for tool in all_tools]}")
        
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(all_tools)
        
        # Get response with potential tool calls
        response = llm_with_tools.invoke(user_query)
        
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
            
            # Create a follow-up message with tool results
            tool_results_text = "\n\n".join([
                f"Tool {result['tool_name']} result:\n{result['result']}"
                for result in tool_results
            ])
            
            follow_up_prompt = f"""
Based on the tool results below, please provide a comprehensive answer to the user's question: "{user_query}"

Tool Results:
{tool_results_text}

Please synthesize this information into a clear, helpful response.
            """.strip()
            
            # Get final response
            final_response = llm.invoke(follow_up_prompt)
            return final_response.content
            
        else:
            # No tool calls needed, return direct response
            logger.info("No tool calls needed, returning direct response")
            return response.content
            
    except Exception as e:
        logger.error(f"Error in direct tool calling: {e}")
        # Fallback to simple RAG
        return chat_query_fallback(user_query)


def chat_query_fallback(user_query: str) -> str:
    """Fallback to simple RAG method."""
    logger.info(f"Using fallback RAG method for: {user_query}")
    
    context = retrieve_campaign_context(user_query)
    if not context:
        return (
            "I'm only able to answer questions about campaign data. "
            "Please ask something related to your campaigns."
        )
    
    response = call_llm(user_query, context)
    return response


def retrieve_campaign_context(user_query: str):
    """Original RAG context retrieval."""
    logger.info(f"Processing query: {user_query}")
    docs = retriever.invoke(user_query)
    if not docs:
        logger.warning(f"No relevant documents found for query: {user_query}")
        return None
    
    logger.info(f"Retrieved {len(docs)} relevant documents")
    
    # Log details about each retrieved document
    for i, doc in enumerate(docs):
        logger.info(f"Document {i+1}:")
        logger.info(f"  Content preview: {doc.page_content[:200]}...")
        if hasattr(doc, 'metadata') and doc.metadata:
            logger.info(f"  Metadata: {doc.metadata}")
        else:
            logger.info("  Metadata: None")
    
    context = "\n".join([doc.page_content for doc in docs])
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
    """Main chat function - uses direct tools with fallback."""
    return chat_query_with_direct_tools(user_query)
