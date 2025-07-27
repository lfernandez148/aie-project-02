# direct_function_calling.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
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
    f"{LOGS_FOLDER}/direct_function_calling.log", 
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

# Mock campaign data
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

@tool
def compare_campaigns(campaign_id1: int, campaign_id2: int) -> str:
    """Compare two campaigns side by side."""
    logger.info(f"Comparing campaigns: {campaign_id1} vs {campaign_id2}")
    
    if campaign_id1 not in CAMPAIGN_DATA or campaign_id2 not in CAMPAIGN_DATA:
        return "One or both campaigns not found."
    
    c1 = CAMPAIGN_DATA[campaign_id1]
    c2 = CAMPAIGN_DATA[campaign_id2]
    
    return f"""
Campaign Comparison:
{campaign_id1} ({c1['name']}) vs {campaign_id2} ({c2['name']})

Revenue: ${c1['revenue']:,} vs ${c2['revenue']:,}
Clicks: {c1['clicks']:,} vs {c2['clicks']:,}
Conversions: {c1['conversions']:,} vs {c2['conversions']:,}
Status: {c1['status']} vs {c2['status']}
        """.strip()

@tool
def search_campaign_documents(query: str) -> str:
    """Search through campaign documents and reports using RAG."""
    logger.info(f"Searching documents for: {query}")
    
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant campaign documents found."
    
    context = "\n".join([doc.page_content for doc in docs])
    return f"Found relevant campaign information:\n\n{context}"

def chat_query_with_direct_tools(user_query: str) -> str:
    """Use direct function calling without agents."""
    logger.info(f"Processing query with direct tools: {user_query}")
    
    try:
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools([
            get_campaign_details,
            calculate_campaign_roi,
            compare_campaigns,
            search_campaign_documents
        ])
        
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
                
                # Execute the appropriate tool
                if tool_name == "get_campaign_details":
                    result = get_campaign_details.invoke(tool_args)
                elif tool_name == "calculate_campaign_roi":
                    result = calculate_campaign_roi.invoke(tool_args)
                elif tool_name == "compare_campaigns":
                    result = compare_campaigns.invoke(tool_args)
                elif tool_name == "search_campaign_documents":
                    result = search_campaign_documents.invoke(tool_args)
                else:
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
    """Main chat function - uses direct tools with fallback."""
    return chat_query_with_direct_tools(user_query)

if __name__ == "__main__":
    # Test the direct function calling
    test_queries = [
        "What's the ROI for campaign 100?",
        "Compare campaigns 100 and 101",
        "Get details for campaign 101",
        "Search for information about holiday campaigns"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print(f"Response: {chat_query(query)}")
        print("-" * 50) 