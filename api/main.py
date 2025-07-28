# api/main.py
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from loguru import logger
import sqlite3
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "../database/sqlite_db/campaigns.db"

# Security
security = HTTPBearer()

# API Keys (in production, store these in a database)
VALID_API_KEYS = {
    "sk-test-1234567890abcdef": {
        "name": "Test API Key",
        "rate_limit": "100/minute",
        "active": True
    },
    "sk-prod-abcdef1234567890": {
        "name": "Production API Key", 
        "rate_limit": "1000/minute",
        "active": True
    }
}

# Load API keys from environment variables
ENV_API_KEYS = os.getenv("API_KEYS", "").split(",")
for key in ENV_API_KEYS:
    if key.strip():
        VALID_API_KEYS[key.strip()] = {
            "name": f"Env API Key {key[:8]}...",
            "rate_limit": "200/minute",
            "active": True
        }

# Configure logging
logger.add(
    "logs/api.log",
    rotation="1 week",
    retention="4 weeks",
    level="INFO"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Campaign Performance API",
    description="Campaign Performance API v2.0 - Secure REST API for campaign data with authentication and rate limiting. Test API Key: sk-test-1234567890abcdef",
    version="2.0.0",
    contact={
        "name": "Campaign Performance API Support",
        "email": "support@campaign-api.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.campaign-performance.com", "description": "Production server"},
    ],
    tags=[
        {"name": "health", "description": "Health check and monitoring endpoints"},
        {"name": "authentication", "description": "Authentication and verification endpoints"},
        {"name": "campaigns", "description": "Campaign data and analytics endpoints"},
        {"name": "analytics", "description": "Summary statistics and top performers"},
        {"name": "comparison", "description": "Campaign comparison endpoints"},
    ]
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Pydantic models for request/response
class CampaignResponse(BaseModel):
    campaign_id: int
    campaign_topic: str
    campaign_date: str
    customer_segment: str
    audience_size: int
    sent: int
    opens: int
    clicks: int
    conversions: int
    open_rate: float
    click_rate: float
    conversion_rate: float

class CampaignSummary(BaseModel):
    campaign_id: int
    campaign_topic: str
    customer_segment: str
    conversion_rate: float
    opens: int
    clicks: int
    conversions: int

class TopCampaignsResponse(BaseModel):
    metric: str
    limit: int
    campaigns: List[CampaignSummary]

class SummaryStatsResponse(BaseModel):
    total_campaigns: int
    average_conversion_rate: float
    average_open_rate: float
    average_click_rate: float
    total_conversions: int
    total_opens: int
    total_clicks: int

class APIKeyInfo(BaseModel):
    name: str
    rate_limit: str
    active: bool

def get_database_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API key from the Authorization header."""
    api_key = credentials.credentials
    
    if api_key not in VALID_API_KEYS:
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key_info = VALID_API_KEYS[api_key]
    if not api_key_info["active"]:
        logger.warning(f"Inactive API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Valid API key used: {api_key_info['name']}")
    return api_key_info

@app.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    """Root endpoint - simple health check."""
    return {
        "status": "healthy",
        "message": "Campaign Performance API is running",
        "version": "2.0.0"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Simple health check endpoint.
    
    Returns basic API status. No authentication required.
    """
    import time
    
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": time.time(),
        "version": "2.0.0"
    }

@app.get("/auth/verify", tags=["authentication"])
async def verify_auth(api_key_info: APIKeyInfo = Depends(verify_api_key)):
    """
    Verify authentication and return API key info.
    
    Use this endpoint to test if your API key is valid and get information about your rate limits.
    """
    return {
        "authenticated": True,
        "api_key_info": api_key_info
    }

@app.get("/campaigns/summary", response_model=SummaryStatsResponse, tags=["analytics"])
@limiter.limit("60/minute")
async def get_campaign_summary_stats(
    request: Request,
    api_key_info: APIKeyInfo = Depends(verify_api_key)
):
    """
    Get summary statistics for all campaigns.
    
    Returns aggregated metrics including total campaigns, average conversion rates,
    and total engagement metrics across all campaigns.
    """
    logger.info(f"API: Getting campaign summary statistics (API Key: {api_key_info['name']})")
    
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
        
        return SummaryStatsResponse(
            total_campaigns=total_campaigns,
            average_conversion_rate=round(avg_conversion, 2),
            average_open_rate=round(avg_open_rate, 2),
            average_click_rate=round(avg_click_rate, 2),
            total_conversions=total_conversions,
            total_opens=total_opens,
            total_clicks=total_clicks
        )
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving summary stats: {str(e)}"
        )
    finally:
        conn.close()

@app.get("/campaigns/top/{metric}", response_model=TopCampaignsResponse, tags=["analytics"])
@limiter.limit("50/minute")
async def get_top_campaigns_by_metric(
    request: Request,
    metric: str,
    limit: int = 5,
    api_key_info: APIKeyInfo = Depends(verify_api_key)
):
    """
    Get top performing campaigns by a specific metric.
    
    Valid metrics: conversion_rate, open_rate, click_rate, opens, clicks, conversions
    """
    logger.info(f"API: Getting top {limit} campaigns by {metric} (API Key: {api_key_info['name']})")
    
    valid_metrics = [
        'conversion_rate', 'open_rate', 'click_rate', 
        'opens', 'clicks', 'conversions'
    ]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Please use one of: {', '.join(valid_metrics)}"
        )
    
    conn = get_database_connection()
    try:
        query = f"""
            SELECT campaign_id, campaign_topic, customer_segment, 
                   conversion_rate, opens, clicks, conversions
            FROM campaigns 
            ORDER BY {metric} DESC 
            LIMIT ?
        """
        results = conn.execute(query, (limit,)).fetchall()
        
        campaigns = []
        for row in results:
            campaigns.append(CampaignSummary(
                campaign_id=row[0],
                campaign_topic=row[1],
                customer_segment=row[2],
                conversion_rate=row[3],
                opens=row[4],
                clicks=row[5],
                conversions=row[6]
            ))
        
        return TopCampaignsResponse(
            metric=metric,
            limit=limit,
            campaigns=campaigns
        )
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving top campaigns: {str(e)}"
        )
    finally:
        conn.close()

@app.get("/campaigns/topic/{topic}", tags=["campaigns"])
@limiter.limit("40/minute")
async def get_campaigns_by_topic(
    request: Request,
    topic: str,
    api_key_info: APIKeyInfo = Depends(verify_api_key)
):
    """
    Get all campaigns for a specific topic.
    
    Searches for campaigns containing the specified topic in their campaign_topic field.
    """
    logger.info(f"API: Getting campaigns for topic: {topic} (API Key: {api_key_info['name']})")
    
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
        
        campaigns = []
        for row in results:
            campaigns.append(CampaignSummary(
                campaign_id=row[0],
                campaign_topic=row[1],
                customer_segment=row[2],
                conversion_rate=row[3],
                opens=row[4],
                clicks=row[5],
                conversions=row[6]
            ))
        
        return {
            "topic": topic,
            "count": len(campaigns),
            "campaigns": campaigns
        }
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaigns: {str(e)}"
        )
    finally:
        conn.close()

@app.get("/campaigns/segment/{segment}", tags=["campaigns"])
@limiter.limit("40/minute")
async def get_campaigns_by_segment(
    request: Request,
    segment: str,
    api_key_info: APIKeyInfo = Depends(verify_api_key)
):
    """
    Get all campaigns for a specific customer segment.
    
    Searches for campaigns targeting the specified customer segment.
    """
    logger.info(f"API: Getting campaigns for segment: {segment} (API Key: {api_key_info['name']})")
    
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
        
        campaigns = []
        for row in results:
            campaigns.append({
                "campaign_id": row[0],
                "campaign_topic": row[1],
                "conversion_rate": row[2],
                "opens": row[3],
                "clicks": row[4],
                "conversions": row[5],
                "campaign_date": row[6]
            })
        
        return {
            "segment": segment,
            "count": len(campaigns),
            "campaigns": campaigns
        }
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaigns: {str(e)}"
        )
    finally:
        conn.close()

@app.get("/campaigns/compare/{campaign_id1}/{campaign_id2}", tags=["comparison"])
@limiter.limit("30/minute")
async def compare_campaigns(
    request: Request,
    campaign_id1: int,
    campaign_id2: int,
    api_key_info: APIKeyInfo = Depends(verify_api_key)
):
    """
    Compare two campaigns side by side.
    
    Returns a detailed comparison of two campaigns by their IDs.
    """
    logger.info(f"API: Comparing campaigns {campaign_id1} and {campaign_id2} (API Key: {api_key_info['name']})")
    
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
            
            return {
                "comparison": f"{campaign_id1} vs {campaign_id2}",
                "campaign_1": {
                    "campaign_id": c1[0],
                    "campaign_topic": c1[1],
                    "customer_segment": c1[2],
                    "conversion_rate": c1[3],
                    "open_rate": c1[4],
                    "click_rate": c1[5],
                    "opens": c1[6],
                    "clicks": c1[7],
                    "conversions": c1[8],
                    "audience_size": c1[9]
                },
                "campaign_2": {
                    "campaign_id": c2[0],
                    "campaign_topic": c2[1],
                    "customer_segment": c2[2],
                    "conversion_rate": c2[3],
                    "open_rate": c2[4],
                    "click_rate": c2[5],
                    "opens": c2[6],
                    "clicks": c2[7],
                    "conversions": c2[8],
                    "audience_size": c2[9]
                }
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="One or both campaigns not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing campaigns: {str(e)}"
        )
    finally:
        conn.close()

@app.get("/campaigns/all", tags=["campaigns"])
@limiter.limit("50/minute")
async def get_all_campaigns(
    request: Request,
    api_key_info: APIKeyInfo = Depends(verify_api_key)
):
    """
    Get all campaigns for data analysis and visualization.
    
    Returns all campaigns with their complete data for charting purposes.
    """
    logger.info(f"API: Getting all campaigns (API Key: {api_key_info['name']})")
    
    conn = get_database_connection()
    try:
        query = """
            SELECT * FROM campaigns 
            ORDER BY campaign_date DESC
        """
        results = conn.execute(query).fetchall()
        
        # Get column names
        columns = [description[0] for description in conn.execute(query).description]
        
        campaigns = []
        for row in results:
            campaign_data = dict(zip(columns, row))
            campaigns.append(campaign_data)
        
        return {
            "count": len(campaigns),
            "campaigns": campaigns
        }
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving all campaigns: {str(e)}"
        )
    finally:
        conn.close()


@app.get("/campaigns/{campaign_id}", response_model=CampaignResponse, tags=["campaigns"])
@limiter.limit("100/minute")
async def get_campaign_by_id(
    request: Request,
    campaign_id: int,
    api_key_info: APIKeyInfo = Depends(verify_api_key)
):
    """
    Get detailed information about a specific campaign by ID.
    
    Returns all available fields for the specified campaign.
    """
    logger.info(f"API: Getting campaign details for ID: {campaign_id} (API Key: {api_key_info['name']})")
    
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
            
            return CampaignResponse(**campaign_data)
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Campaign {campaign_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving campaign {campaign_id}: {str(e)}"
        )
    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 