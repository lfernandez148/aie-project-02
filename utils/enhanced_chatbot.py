# enhanced_chatbot.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from loguru import logger
from dotenv import load_dotenv
import os

# Import database tools
from database_tools import DATABASE_TOOLS
from database_setup import get_database_connection

load_dotenv()

CHROMA_DIR = "../chroma_db"
LOGS_FOLDER = "../logs"

# Configuration: Choose between OpenAI and LM Studio
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LM_STUDIO_URL = "http://localhost:1234"

logger.add(
    f"{LOGS_FOLDER}/enhanced_chatbot.log", 
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
        api_key="not-needed",
        temperature=0,
        model="local-model"
    )
else:
    logger.info("Using OpenAI")
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo"
    )

@tool
def search_campaign_documents(query: str) -> str:
    """Search through campaign documents and reports using RAG."""
    logger.info(f"Searching documents for: {query}")
    
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant campaign documents found."
    
    context = "\n".join([doc.page_content for doc in docs])
    return f"Found relevant campaign information:\n\n{context}"

def create_enhanced_agent():
    """Create an agent with both RAG and database tools."""
    
    # Combine RAG tool with database tools
    all_tools = [search_campaign_documents] + DATABASE_TOOLS
    
    logger.info(f"Creating agent with {len(all_tools)} tools")
    
    agent = initialize_agent(
        tools=all_tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent

def chat_query_enhanced(user_query: str) -> str:
    """Enhanced chat function that uses both RAG and database tools."""
    logger.info(f"Processing enhanced query: {user_query}")
    
    try:
        agent = create_enhanced_agent()
        response = agent.invoke({"input": user_query})
        return response["output"]
    except Exception as e:
        logger.error(f"Error in enhanced query: {e}")
        # Fallback to original RAG method
        return chat_query_fallback(user_query)

def chat_query_fallback(user_query: str) -> str:
    """Fallback to original RAG method if tools fail."""
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
    
    context = "\n".join([doc.page_content for doc in docs])
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
    return response.content.strip()

# For backward compatibility
def chat_query(user_query: str) -> str:
    """Main chat function - uses enhanced tools with fallback."""
    return chat_query_enhanced(user_query)

if __name__ == "__main__":
    # Test the enhanced chatbot
    test_queries = [
        "What's the conversion rate for campaign 100?",
        "Search for information about holiday campaigns",
        "Show me the top 5 campaigns by conversion rate",
        "Compare campaigns 100 and 101",
        "What campaigns target Women 25-34?",
        "Get summary statistics for all campaigns"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print(f"Response: {chat_query(query)}")
        print("-" * 50) 