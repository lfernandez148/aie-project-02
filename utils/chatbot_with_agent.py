# chatbot_with_agent.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from loguru import logger
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_DIR = "../chroma_db"
LOGS_FOLDER = "../logs"

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

# Mock campaign data (in real app, this would be from database/API)
CAMPAIGN_DATA = {
    100: {
        "name": "Summer Sale 2024",
        "revenue": 15000,
        "clicks": 2500,
        "conversions": 150,
        "status": "active"
    },
    101: {
        "name": "Winter Collection",
        "revenue": 8000,
        "clicks": 1200,
        "conversions": 80,
        "status": "completed"
    }
}


@tool
def search_campaign_documents(query: str) -> str:
    """Search through campaign documents and reports using RAG."""
    logger.info(f"Searching documents for: {query}")
    
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant campaign documents found."
    
    context = "\n".join([doc.page_content for doc in docs])
    return f"Found relevant campaign information:\n\n{context}"


@tool
def get_campaign_details(campaign_id: int) -> str:
    """Get detailed information about a specific campaign by ID."""
    logger.info(f"Getting details for campaign: {campaign_id}")
    
    if campaign_id in CAMPAIGN_DATA:
        campaign = CAMPAIGN_DATA[campaign_id]
        return f"""
Campaign: {campaign['name']}
Revenue: ${campaign['revenue']:,}
Clicks: {campaign['clicks']:,}
Conversions: {campaign['conversions']:,}
Status: {campaign['status']}
        """.strip()
    else:
        return f"Campaign {campaign_id} not found."


@tool
def calculate_campaign_roi(campaign_id: int) -> str:
    """Calculate Return on Investment for a campaign."""
    logger.info(f"Calculating ROI for campaign: {campaign_id}")
    
    if campaign_id in CAMPAIGN_DATA:
        campaign = CAMPAIGN_DATA[campaign_id]
        cost = campaign['clicks'] * 2  # $2 per click
        roi = ((campaign['revenue'] - cost) / cost) * 100
        
        return f"""
Campaign ROI Analysis:
Revenue: ${campaign['revenue']:,}
Cost: ${cost:,}
ROI: {roi:.1f}%
        """.strip()
    else:
        return f"Campaign {campaign_id} not found."


def create_enhanced_agent():
    """Create an agent with both RAG and function calling capabilities."""
    tools = [
        search_campaign_documents,
        get_campaign_details,
        calculate_campaign_roi
    ]
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent


def chat_query_with_agent(user_query: str) -> str:
    """Enhanced chat function that uses agents with RAG and tools."""
    logger.info(f"Processing query with agent: {user_query}")
    
    try:
        agent = create_enhanced_agent()
        response = agent.invoke({"input": user_query})
        return response["output"]
    except Exception as e:
        logger.error(f"Error in agent-based query: {e}")
        # Fallback to original RAG method
        return chat_query_fallback(user_query)


def chat_query_fallback(user_query: str) -> str:
    """Fallback to original RAG method if agent fails."""
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
    """Main chat function - uses enhanced agent with fallback."""
    return chat_query_with_agent(user_query)


if __name__ == "__main__":
    # Test the enhanced chatbot
    test_queries = [
        "What's the ROI for campaign 100?",
        "Search for information about summer campaigns",
        "Compare campaign 100 and 101"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print(f"Response: {chat_query(query)}")
        print("-" * 50) 