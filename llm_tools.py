# llm_tools.py
from langchain.tools import tool
from database.database_setup import get_database_connection
from loguru import logger
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import sqlite3

# Load the persisted Chroma DB and retriever for RAG
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 4})

DB_PATH = "database/sqlite_db/campaigns.db"


def get_database_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


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
    
    conn = get_database_connection()
    try:
        query = """
            SELECT * FROM campaigns 
            WHERE campaign_id = ?
        """
        result = conn.execute(query, (campaign_id,)).fetchone()
        
        if result:
            # Get column names
            columns = [
                description[0] for description in 
                conn.execute(query, (campaign_id,)).description
            ]
            campaign_data = dict(zip(columns, result))
            
            return f"""
Campaign {campaign_id} Details:
- Topic: {campaign_data['campaign_topic']}
- Date: {campaign_data['campaign_date']}
- Customer Segment: {campaign_data['customer_segment']}
- Audience Size: {campaign_data['audience_size']:,}
- Sent: {campaign_data['sent']:,}
- Opens: {campaign_data['opens']:,}
- Clicks: {campaign_data['clicks']:,}
- Conversions: {campaign_data['conversions']:,}
- Open Rate: {campaign_data['open_rate']}%
- Click Rate: {campaign_data['click_rate']}%
- Conversion Rate: {campaign_data['conversion_rate']}%
            """.strip()
        else:
            return f"Campaign {campaign_id} not found."
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        return f"Error retrieving campaign {campaign_id}: {e}"
    finally:
        conn.close()


@tool
def get_top_campaigns_by_metric(metric: str, limit: int = 5) -> str:
    """Get top performing campaigns by a specific metric."""
    logger.info(f"Getting top {limit} campaigns by {metric}")
    
    valid_metrics = [
        'conversion_rate', 'open_rate', 'click_rate', 
        'opens', 'clicks', 'conversions'
    ]
    if metric not in valid_metrics:
        return f"Invalid metric. Please use one of: {', '.join(valid_metrics)}"
    
    conn = get_database_connection()
    try:
        query = f"""
            SELECT campaign_id, campaign_topic, customer_segment, {metric}
            FROM campaigns 
            ORDER BY {metric} DESC 
            LIMIT ?
        """
        results = conn.execute(query, (limit,)).fetchall()
        
        if results:
            response = f"Top {limit} campaigns by {metric}:\n\n"
            for i, row in enumerate(results, 1):
                response += f"{i}. Campaign {row[0]} ({row[1]})\n"
                response += f"   Segment: {row[2]}\n"
                metric_title = metric.replace('_', ' ').title()
                response += f"   {metric_title}: {row[3]}\n\n"
            return response.strip()
        else:
            return "No campaigns found."
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        return f"Error retrieving top campaigns: {e}"
    finally:
        conn.close()


@tool
def get_campaigns_by_topic(topic: str) -> str:
    """Get all campaigns for a specific topic."""
    logger.info(f"Getting campaigns for topic: {topic}")
    
    conn = get_database_connection()
    try:
        query = """
            SELECT campaign_id, campaign_topic, customer_segment, 
                   conversion_rate, opens, clicks, conversions
            FROM campaigns 
            WHERE campaign_topic LIKE ?
            ORDER BY conversion_rate DESC
        """
        results = conn.execute(query, (f'%{topic}%',)).fetchall()
        
        if results:
            response = f"Campaigns for topic '{topic}':\n\n"
            for row in results:
                response += f"Campaign {row[0]}:\n"
                response += f"  Segment: {row[2]}\n"
                response += f"  Conversion Rate: {row[3]}%\n"
                response += (
                    f"  Opens: {row[4]:,}, Clicks: {row[5]:,}, "
                    f"Conversions: {row[6]:,}\n\n"
                )
            return response.strip()
        else:
            return f"No campaigns found for topic '{topic}'."
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        return f"Error retrieving campaigns: {e}"
    finally:
        conn.close()


@tool
def get_campaigns_by_segment(segment: str) -> str:
    """Get all campaigns for a specific customer segment."""
    logger.info(f"Getting campaigns for segment: {segment}")
    
    conn = get_database_connection()
    try:
        query = """
            SELECT campaign_id, campaign_topic, conversion_rate, 
                   opens, clicks, conversions, campaign_date
            FROM campaigns 
            WHERE customer_segment LIKE ?
            ORDER BY campaign_date DESC
        """
        results = conn.execute(query, (f'%{segment}%',)).fetchall()
        
        if results:
            response = f"Campaigns for segment '{segment}':\n\n"
            for row in results:
                response += f"Campaign {row[0]} ({row[6]}):\n"
                response += f"  Topic: {row[1]}\n"
                response += f"  Conversion Rate: {row[2]}%\n"
                response += (
                    f"  Opens: {row[3]:,}, Clicks: {row[4]:,}, "
                    f"Conversions: {row[5]:,}\n\n"
                )
            return response.strip()
        else:
            return f"No campaigns found for segment '{segment}'."
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        return f"Error retrieving campaigns: {e}"
    finally:
        conn.close()


@tool
def get_campaign_summary_stats() -> str:
    """Get summary statistics for all campaigns."""
    logger.info("Getting campaign summary statistics")
    
    conn = get_database_connection()
    try:
        # Get various summary stats
        total_campaigns = conn.execute(
            "SELECT COUNT(*) FROM campaigns"
        ).fetchone()[0]
        avg_conversion = conn.execute(
            "SELECT AVG(conversion_rate) FROM campaigns"
        ).fetchone()[0]
        avg_open_rate = conn.execute(
            "SELECT AVG(open_rate) FROM campaigns"
        ).fetchone()[0]
        avg_click_rate = conn.execute(
            "SELECT AVG(click_rate) FROM campaigns"
        ).fetchone()[0]
        total_conversions = conn.execute(
            "SELECT SUM(conversions) FROM campaigns"
        ).fetchone()[0]
        total_opens = conn.execute(
            "SELECT SUM(opens) FROM campaigns"
        ).fetchone()[0]
        total_clicks = conn.execute(
            "SELECT SUM(clicks) FROM campaigns"
        ).fetchone()[0]
        
        return f"""
Campaign Summary Statistics:
- Total Campaigns: {total_campaigns:,}
- Average Conversion Rate: {avg_conversion:.2f}%
- Average Open Rate: {avg_open_rate:.2f}%
- Average Click Rate: {avg_click_rate:.2f}%
- Total Conversions: {total_conversions:,}
- Total Opens: {total_opens:,}
- Total Clicks: {total_clicks:,}
        """.strip()
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return f"Error retrieving summary stats: {e}"
    finally:
        conn.close()


@tool
def compare_campaigns_by_id(campaign_id1: int, campaign_id2: int) -> str:
    """Compare two campaigns side by side."""
    logger.info(f"Comparing campaigns {campaign_id1} and {campaign_id2}")
    
    conn = get_database_connection()
    try:
        query = """
            SELECT campaign_id, campaign_topic, customer_segment, 
                   conversion_rate, open_rate, click_rate,
                   opens, clicks, conversions, audience_size
            FROM campaigns 
            WHERE campaign_id IN (?, ?)
            ORDER BY campaign_id
        """
        results = conn.execute(query, (campaign_id1, campaign_id2)).fetchall()
        
        if len(results) == 2:
            c1, c2 = results[0], results[1]
            
            return f"""
Campaign Comparison:
{campaign_id1} vs {campaign_id2}

Campaign {c1[0]} ({c1[1]}):
  Segment: {c1[2]}
  Conversion Rate: {c1[3]}%
  Open Rate: {c1[4]}%
  Click Rate: {c1[5]}%
  Opens: {c1[6]:,}, Clicks: {c1[7]:,}, Conversions: {c1[8]:,}
  Audience: {c1[9]:,}

Campaign {c2[0]} ({c2[1]}):
  Segment: {c2[2]}
  Conversion Rate: {c2[3]}%
  Open Rate: {c2[4]}%
  Click Rate: {c2[5]}%
  Opens: {c2[6]:,}, Clicks: {c2[7]:,}, Conversions: {c2[8]:,}
  Audience: {c2[9]:,}
            """.strip()
        else:
            return "One or both campaigns not found."
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        return f"Error comparing campaigns: {e}"
    finally:
        conn.close()


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