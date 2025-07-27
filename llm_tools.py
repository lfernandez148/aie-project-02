# llm_tools.py
from langchain.tools import tool
from database.database_setup import get_database_connection
from loguru import logger
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import requests
import json

# Load the persisted Chroma DB and retriever for RAG
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 4})

# FastAPI base URL
API_BASE_URL = "http://localhost:8000"

# API Key for authentication
API_KEY = "sk-test-1234567890abcdef"


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
def get_campaign_by_id(campaign_id: int) -> str:
    """Get detailed information about a specific campaign by ID."""
    logger.info(f"Getting campaign details for ID: {campaign_id}")
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{API_BASE_URL}/campaigns/{campaign_id}", headers=headers)
        if response.status_code == 200:
            campaign = response.json()
            return f"""
Campaign {campaign_id} Details:
- Topic: {campaign['campaign_topic']}
- Date: {campaign['campaign_date']}
- Customer Segment: {campaign['customer_segment']}
- Audience Size: {campaign['audience_size']:,}
- Sent: {campaign['sent']:,}
- Opens: {campaign['opens']:,}
- Clicks: {campaign['clicks']:,}
- Conversions: {campaign['conversions']:,}
- Open Rate: {campaign['open_rate']}%
- Click Rate: {campaign['click_rate']}%
- Conversion Rate: {campaign['conversion_rate']}%
            """.strip()
        else:
            return f"Campaign {campaign_id} not found."
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"Error retrieving campaign {campaign_id}: {e}"


@tool
def get_top_campaigns_by_metric(metric: str, limit: int = 5) -> str:
    """Get top performing campaigns by a specific metric."""
    logger.info(f"Getting top {limit} campaigns by {metric}")
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(
            f"{API_BASE_URL}/campaigns/top/{metric}?limit={limit}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            result = f"Top {data['limit']} campaigns by {data['metric']}:\n\n"
            for i, campaign in enumerate(data['campaigns'], 1):
                result += f"{i}. Campaign {campaign['campaign_id']} ({campaign['campaign_topic']})\n"
                result += f"   Segment: {campaign['customer_segment']}\n"
                result += f"   Conversion Rate: {campaign['conversion_rate']}%\n\n"
            return result.strip()
        else:
            return f"Error: {response.json()['detail']}"
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"Error retrieving top campaigns: {e}"


@tool
def get_campaigns_by_topic(topic: str) -> str:
    """Get all campaigns for a specific topic."""
    logger.info(f"Getting campaigns for topic: {topic}")
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{API_BASE_URL}/campaigns/topic/{topic}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            result = f"Campaigns for topic '{topic}' ({data['count']} found):\n\n"
            for campaign in data['campaigns']:
                result += f"Campaign {campaign['campaign_id']}:\n"
                result += f"  Segment: {campaign['customer_segment']}\n"
                result += f"  Conversion Rate: {campaign['conversion_rate']}%\n"
                result += f"  Opens: {campaign['opens']:,}, Clicks: {campaign['clicks']:,}, Conversions: {campaign['conversions']:,}\n\n"
            return result.strip()
        else:
            return f"Error: {response.json()['detail']}"
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"Error retrieving campaigns: {e}"


@tool
def get_campaigns_by_segment(segment: str) -> str:
    """Get all campaigns for a specific customer segment."""
    logger.info(f"Getting campaigns for segment: {segment}")
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{API_BASE_URL}/campaigns/segment/{segment}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            result = f"Campaigns for segment '{segment}' ({data['count']} found):\n\n"
            for campaign in data['campaigns']:
                result += f"Campaign {campaign['campaign_id']} ({campaign['campaign_date']}):\n"
                result += f"  Topic: {campaign['campaign_topic']}\n"
                result += f"  Conversion Rate: {campaign['conversion_rate']}%\n"
                result += f"  Opens: {campaign['opens']:,}, Clicks: {campaign['clicks']:,}, Conversions: {campaign['conversions']:,}\n\n"
            return result.strip()
        else:
            return f"Error: {response.json()['detail']}"
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"Error retrieving campaigns: {e}"


@tool
def get_campaign_summary_stats() -> str:
    """Get summary statistics for all campaigns."""
    logger.info("Getting campaign summary statistics")
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{API_BASE_URL}/campaigns/summary", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            return f"""
Campaign Summary Statistics:
- Total Campaigns: {stats['total_campaigns']:,}
- Average Conversion Rate: {stats['average_conversion_rate']}%
- Average Open Rate: {stats['average_open_rate']}%
- Average Click Rate: {stats['average_click_rate']}%
- Total Conversions: {stats['total_conversions']:,}
- Total Opens: {stats['total_opens']:,}
- Total Clicks: {stats['total_clicks']:,}
            """.strip()
        else:
            return f"Error: {response.json()['detail']}"
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"Error retrieving summary stats: {e}"


@tool
def compare_campaigns_by_id(campaign_id1: int, campaign_id2: int) -> str:
    """Compare two campaigns side by side."""
    logger.info(f"Comparing campaigns {campaign_id1} and {campaign_id2}")
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{API_BASE_URL}/campaigns/compare/{campaign_id1}/{campaign_id2}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            c1, c2 = data['campaign_1'], data['campaign_2']
            
            return f"""
Campaign Comparison:
{campaign_id1} vs {campaign_id2}

Campaign {c1['campaign_id']} ({c1['campaign_topic']}):
  Segment: {c1['customer_segment']}
  Conversion Rate: {c1['conversion_rate']}%
  Open Rate: {c1['open_rate']}%
  Click Rate: {c1['click_rate']}%
  Opens: {c1['opens']:,}, Clicks: {c1['clicks']:,}, Conversions: {c1['conversions']:,}
  Audience: {c1['audience_size']:,}

Campaign {c2['campaign_id']} ({c2['campaign_topic']}):
  Segment: {c2['customer_segment']}
  Conversion Rate: {c2['conversion_rate']}%
  Open Rate: {c2['open_rate']}%
  Click Rate: {c2['click_rate']}%
  Opens: {c2['opens']:,}, Clicks: {c2['clicks']:,}, Conversions: {c2['conversions']:,}
  Audience: {c2['audience_size']:,}
            """.strip()
        else:
            return f"Error: {response.json()['detail']}"
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"Error comparing campaigns: {e}"


# List of all available tools for the LLM
LLM_TOOLS = [
    search_campaign_documents,
    get_campaign_by_id,
    get_top_campaigns_by_metric,
    get_campaigns_by_topic,
    get_campaigns_by_segment,
    get_campaign_summary_stats,
    compare_campaigns_by_id
] 