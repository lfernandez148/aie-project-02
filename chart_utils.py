# chart_utils.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from loguru import logger
import uuid

# FastAPI base URL and API Key
API_BASE_URL = "http://localhost:8000"
API_KEY = "sk-test-1234567890abcdef"


def get_campaign_data():
    """Fetch campaign data from the API."""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{API_BASE_URL}/campaigns/summary", headers=headers)
        
        if response.status_code == 200:
            # Get all campaigns for detailed analysis
            campaigns_response = requests.get(
                f"{API_BASE_URL}/campaigns/all", 
                headers=headers
            )
            
            if campaigns_response.status_code == 200:
                campaigns_data = campaigns_response.json()
                return pd.DataFrame(campaigns_data['campaigns'])
            else:
                logger.error(f"Failed to get campaigns: {campaigns_response.status_code}")
                return None
        else:
            logger.error(f"Failed to get summary: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching campaign data: {e}")
        return None


def create_audience_by_topic_chart():
    """Create a basic bar chart showing audience volume by campaign topic."""
    df = get_campaign_data()
    if df is None or df.empty:
        st.error("Unable to fetch campaign data for visualization.")
        return None
    topic_audience = df.groupby('campaign_topic')['audience_size'].sum().reset_index()
    topic_audience = topic_audience.sort_values('audience_size', ascending=False)
    fig = px.bar(
        topic_audience,
        x='campaign_topic',
        y='audience_size',
        title='Target Audience Volume by Campaign Topic',
        labels={'campaign_topic': 'Campaign Topic', 'audience_size': 'Audience Size'}
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )
    return fig


def create_conversion_rate_chart():
    """Create a basic bar chart showing conversion rates by campaign."""
    df = get_campaign_data()
    if df is None or df.empty:
        st.error("Unable to fetch campaign data for visualization.")
        return None
    df_sorted = df.sort_values('conversion_rate', ascending=False).head(10)
    fig = px.bar(
        df_sorted,
        x='campaign_topic',
        y='conversion_rate',
        title='Top 10 Campaigns by Conversion Rate',
        labels={'campaign_topic': 'Campaign Topic', 'conversion_rate': 'Conversion Rate (%)'}
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )
    return fig


def create_segment_performance_chart():
    """Create a basic bar chart showing performance by customer segment."""
    df = get_campaign_data()
    if df is None or df.empty:
        st.error("Unable to fetch campaign data for visualization.")
        return None
    segment_performance = df.groupby('customer_segment').agg({
        'conversion_rate': 'mean',
        'open_rate': 'mean',
        'click_rate': 'mean',
        'audience_size': 'sum'
    }).reset_index()
    fig = px.bar(
        segment_performance,
        x='customer_segment',
        y='conversion_rate',
        title='Average Conversion Rate by Customer Segment',
        labels={'customer_segment': 'Customer Segment', 'conversion_rate': 'Avg Conversion Rate (%)'}
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )
    return fig


def create_trend_chart():
    """Create a basic line chart showing trends over time."""
    df = get_campaign_data()
    if df is None or df.empty:
        st.error("Unable to fetch campaign data for visualization.")
        return None
    df['campaign_date'] = pd.to_datetime(df['campaign_date'])
    daily_trends = df.groupby('campaign_date').agg({
        'conversion_rate': 'mean',
        'open_rate': 'mean',
        'click_rate': 'mean'
    }).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_trends['campaign_date'],
        y=daily_trends['conversion_rate'],
        mode='lines+markers',
        name='Conversion Rate',
        line=dict(color='black', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=daily_trends['campaign_date'],
        y=daily_trends['open_rate'],
        mode='lines+markers',
        name='Open Rate',
        line=dict(color='gray', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=daily_trends['campaign_date'],
        y=daily_trends['click_rate'],
        mode='lines+markers',
        name='Click Rate',
        line=dict(color='lightgray', width=2)
    ))
    fig.update_layout(
        title='Campaign Performance Trends Over Time',
        xaxis_title='Date',
        yaxis_title='Rate (%)',
        height=500,
        hovermode='x unified',
        showlegend=True
    )
    return fig


def display_chart(chart_type: str):
    """Display a specific chart based on the chart type."""
    unique_key = f"{chart_type}-{uuid.uuid4()}"
    if chart_type == "audience_by_topic":
        fig = create_audience_by_topic_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=unique_key)
    elif chart_type == "conversion_rate":
        fig = create_conversion_rate_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=unique_key)
    elif chart_type == "segment_performance":
        fig = create_segment_performance_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=unique_key)
    elif chart_type == "trends":
        fig = create_trend_chart()
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=unique_key)
    # No return value


def get_available_charts():
    """Get list of available chart types."""
    return [
        "audience_by_topic",
        "conversion_rate", 
        "segment_performance",
        "trends"
    ] 