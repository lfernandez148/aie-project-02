# llm_tools.py
from langchain.tools import tool
from loguru import logger
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import requests
from chart_utils import get_available_charts
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI configuration from environment
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "sk-test-1234567890abcdef")

def make_api_request(endpoint: str, method: str = "GET") -> dict:
    """Helper function to make API requests with consistent error handling."""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.content else 'API error'
            return {"success": False, "error": error_detail, "status_code": response.status_code}
            
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {"success": False, "error": f"Network error: {e}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"success": False, "error": f"Unexpected error: {e}"}


@tool
def search_campaign_documents(query: str) -> dict:
    """Search for campaign information in uploaded documents (PDFs, HTML, DOCX files). 
    Use this when users ask about executive summaries, performance insights, 
    recommendations, or any content that would be in campaign reports/documents.
    Examples: "executive summary for campaign 101", "performance insights", 
    "recommendations for campaign 102", "what does the report say about..."
    """
    logger.info(f"search_campaign_documents")
    logger.info(f"Searching documents for: {query}")
    
    # Get campaign_id from query if present
    match = re.search(r'campaign\s+(\d+)', query, re.IGNORECASE)
    campaign_id = match.group(1) if match else None
    logger.info(f"campaign_id: {campaign_id}")

    search_kwargs = {"k": 4}
    if campaign_id:
        search_kwargs["filter"] = {"campaign_id": f"{campaign_id}"}
        print("search_kwargs:", search_kwargs)
        
    # Use similarity search with scores to filter relevant documents
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    docs_and_scores = db.similarity_search_with_score(query, **search_kwargs)
    
    # Filter documents with similarity score above threshold
    relevant_docs = []
    sources = []
    for doc, score in docs_and_scores:
        logger.info(f"Document similarity score: {score:.4f}")
        # For cosine distance: 0 = identical, 1 = orthogonal, 2 = opposite
        # Use a more reasonable threshold for cosine distance
        if score < 1.2:  # More reasonable threshold for cosine distance
            relevant_docs.append(doc)
            # Extract source from metadata or document attributes
            source = "Unknown document"
            if hasattr(doc, 'metadata') and doc.metadata:
                source = doc.metadata.get('source', 'Unknown document')
            elif hasattr(doc, 'source'):
                source = doc.source
            else:
                # Try to extract filename from metadata if available
                if hasattr(doc, 'metadata') and doc.metadata:
                    # Look for any metadata that might contain file info
                    for key, value in doc.metadata.items():
                        if 'source' in key.lower() or 'file' in key.lower():
                            source = str(value)
                            break
            sources.append(source)
        else:
            logger.info(f"Document filtered out due to high score: {score:.4f}")
    
    if not relevant_docs:
        logger.info("No documents met similarity threshold")
        return {
            "type": "text",
            "message": "No relevant campaign documents found.",
            "source": "Vector Database (no relevant documents)"
        }
    
    logger.info(f"Found {len(relevant_docs)} relevant documents")
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    # Create source information
    unique_sources = list(set(sources))
    source_info = f"Vector Database ({', '.join(unique_sources)})"
    logger.info(f"source_info: {source_info}")
    
    return {
        "type": "text",
        "message": f"Found relevant campaign information:\n\n{context}",
        "source": source_info
    }


@tool
def get_campaign_by_id(campaign_id: int) -> dict:
    """Get structured campaign data from the database for a specific campaign ID.
    Use this when users ask for specific metrics, numbers, or structured data 
    about a campaign (opens, clicks, conversion rates, audience size, etc.).
    Examples: "campaign 101 metrics", "how many opens did campaign 102 get", 
    "what is the conversion rate for campaign 103", "audience size for campaign 104"
    """
    logger.info(f"Getting campaign details for ID: {campaign_id}")
    
    result = make_api_request(f"/campaigns/{campaign_id}")
    
    if result["success"]:
        campaign = result["data"]
        return {
            "type": "text",
            "message": f"""
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
            """.strip(),
            "source": "Campaign Database (campaigns table)"
        }
    else:
        return {
            "type": "text",
            "message": f"Campaign {campaign_id} not found: {result['error']}",
            "source": "Campaign Database (API error)"
        }


@tool
def get_top_campaigns_by_metric(metric: str = '', limit: int = 5) -> dict:
    """Get top performing campaigns by a specific metric and return as a table.
    Use this when users ask for "top campaigns", "best performing", "rankings", 
    "table of campaigns", or want to compare campaigns by a specific metric.
    Examples: "top 5 campaigns by conversion rate", "best campaigns by opens",
    "show me the top campaigns", "rank campaigns by clicks", 
    "show me a table of top 10 campaigns by conversion rate",
    "table of top campaigns by opens", "top campaigns table"
    """
    if not metric:
        metric = 'opens'
    logger.info(f"Getting top {limit} campaigns by {metric}")
    
    result = make_api_request(f"/campaigns/top/{metric}?limit={limit}")
    
    if result["success"]:
        data = result["data"]
        table_result = {
            "type": "table",
            "columns": ["campaign_id", "campaign_topic", "customer_segment", 
                       "conversion_rate"],
            "rows": [
                {
                    "campaign_id": c["campaign_id"],
                    "campaign_topic": c["campaign_topic"],
                    "customer_segment": c["customer_segment"],
                    "conversion_rate": c["conversion_rate"],
                }
                for c in data["campaigns"]
            ],
            "message": f"Top {data['limit']} campaigns by {data['metric']}:",
            "source": "Campaign Database (campaigns table)"
        }
        logger.info(f"Returning table dict: {table_result}")
        return table_result
    else:
        return {
            "type": "error",
            "message": f"Error: {result['error']}",
            "source": "Campaign Database (API error)"
        }


@tool
def get_campaigns_by_topic(topic: str) -> dict:
    """Get all campaigns for a specific topic from the database.
    Use this when users ask about campaigns by topic, theme, or subject.
    Examples: "campaigns about loyalty", "fitness campaigns", "promotional campaigns",
    "show me all campaigns for topic X"
    """
    logger.info(f"Getting campaigns for topic: {topic}")
    
    result = make_api_request(f"/campaigns/topic/{topic}")
    
    if result["success"]:
        data = result["data"]
        message = f"Campaigns for topic '{topic}' ({data['count']} found):\n\n"
        for campaign in data['campaigns']:
            message += f"Campaign {campaign['campaign_id']}:\n"
            message += f"  Segment: {campaign['customer_segment']}\n"
            message += f"  Conversion Rate: {campaign['conversion_rate']}%\n"
            message += f"  Opens: {campaign['opens']:,}, Clicks: {campaign['clicks']:,}, Conversions: {campaign['conversions']:,}\n\n"
        return {
            "type": "text",
            "message": message.strip(),
            "source": "Campaign Database (campaigns table)"
        }
    else:
        return {
            "type": "text",
            "message": f"Error retrieving campaigns for topic '{topic}': {result['error']}",
            "source": "Campaign Database (API error)"
        }


@tool
def get_campaigns_by_segment(segment: str) -> dict:
    """Get all campaigns for a specific customer segment from the database.
    Use this when users ask about campaigns by audience, customer type, or segment.
    Examples: "campaigns for fitness enthusiasts", "retail customer campaigns",
    "previous customer campaigns", "show me campaigns for segment X"
    """
    logger.info(f"Getting campaigns for segment: {segment}")
    
    result = make_api_request(f"/campaigns/segment/{segment}")
    
    if result["success"]:
        data = result["data"]
        message = f"Campaigns for segment '{segment}' ({data['count']} found):\n\n"
        for campaign in data['campaigns']:
            message += f"Campaign {campaign['campaign_id']} ({campaign['campaign_date']}):\n"
            message += f"  Topic: {campaign['campaign_topic']}\n"
            message += f"  Conversion Rate: {campaign['conversion_rate']}%\n"
            message += f"  Opens: {campaign['opens']:,}, Clicks: {campaign['clicks']:,}, Conversions: {campaign['conversions']:,}\n\n"
        return {
            "type": "text",
            "message": message.strip(),
            "source": "Campaign Database (campaigns table)"
        }
    else:
        return {
            "type": "text",
            "message": f"Error retrieving campaigns for segment '{segment}': {result['error']}",
            "source": "Campaign Database (API error)"
        }


@tool
def get_campaign_summary_stats() -> dict:
    """Get summary statistics for all campaigns from the database.
    Use this when users ask for overall statistics, averages, totals, or summary data.
    Examples: "summary statistics", "overall campaign performance", "average metrics",
    "total campaign stats", "how are all campaigns performing"
    """
    logger.info("Getting campaign summary statistics")
    
    result = make_api_request("/campaigns/summary")
    
    if result["success"]:
        stats = result["data"]
        return {
            "type": "text",
            "message": f"""
Campaign Summary Statistics:
- Total Campaigns: {stats['total_campaigns']:,}
- Average Conversion Rate: {stats['average_conversion_rate']}%
- Average Open Rate: {stats['average_open_rate']}%
- Average Click Rate: {stats['average_click_rate']}%
- Total Conversions: {stats['total_conversions']:,}
- Total Opens: {stats['total_opens']:,}
- Total Clicks: {stats['total_clicks']:,}
            """.strip(),
            "source": "Campaign Database (campaigns table)"
        }
    else:
        return {
            "type": "text",
            "message": f"Error retrieving summary statistics: {result['error']}",
            "source": "Campaign Database (API error)"
        }


@tool
def compare_campaigns_by_id(campaign_id1: int, campaign_id2: int) -> dict:
    """Compare two campaigns side by side from the database.
    Use this when users want to compare two specific campaigns or see differences.
    Examples: "compare campaign 101 and 102", "campaign 101 vs 102", 
    "how do campaigns 103 and 104 compare", "difference between campaign X and Y"
    """
    logger.info(f"Comparing campaigns {campaign_id1} and {campaign_id2}")
    
    result = make_api_request(f"/campaigns/compare/{campaign_id1}/{campaign_id2}")
    
    if result["success"]:
        data = result["data"]
        c1, c2 = data['campaign_1'], data['campaign_2']
        
        return {
            "type": "text",
            "message": f"""
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
            """.strip(),
            "source": "Campaign Database (campaigns table)"
        }
    else:
        return {
            "type": "text",
            "message": f"Error comparing campaigns: {result['error']}",
            "source": "Campaign Database (API error)"
        }


@tool
def create_campaign_chart(chart_type: str) -> dict:
    """Create and display a chart for campaign data visualization.
    
    Available chart types:
    - audience_by_topic: Bar chart showing audience volume by campaign topic
    - conversion_rate: Bar chart showing top campaigns by conversion rate
    - segment_performance: Bar chart showing performance by customer segment
    - trends: Line chart showing performance trends over time
    """
    logger.info(f"Creating chart: {chart_type}")
    
    available_charts = get_available_charts()
    if chart_type not in available_charts:
        return {
            "type": "error",
            "message": f"Invalid chart type. Available types: {', '.join(available_charts)}",
            "source": "Chart Generation Tool"
        }
    # Do NOT call display_chart here. Just return the chart type and message.
    return {
        "type": "chart",
        "chart_type": chart_type,
        "message": f"📊 {chart_type.replace('_', ' ').title()}",
        "source": "Chart Generation Tool (Plotly + Campaign Database)"
    }


# List of all available tools for the LLM
LLM_TOOLS = [
    search_campaign_documents,
    get_campaign_by_id,
    get_top_campaigns_by_metric,
    get_campaigns_by_topic,
    get_campaigns_by_segment,
    get_campaign_summary_stats,
    compare_campaigns_by_id,
    create_campaign_chart
] 