"""AI-powered insights using Claude API."""
import os
from anthropic import Anthropic
import streamlit as st
from typing import Dict, Optional
import pandas as pd

def get_claude_client() -> Optional[Anthropic]:
    """Initialize Claude API client with proper error handling.
    
    Returns:
        Anthropic client if valid API key, None otherwise.
    
    Note:
        OAuth tokens (sk-ant-oat01-*) from Claude Max subscriptions do NOT work
        as regular API keys. Only standard API keys (sk-ant-api03-*) are supported.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    
    # Check if this is an OAuth token (not supported for API access)
    if api_key.startswith("sk-ant-oat01-"):
        st.warning(
            "⚠️ **AI Insights Unavailable**: The configured API key is a Claude Max "
            "OAuth token, which cannot be used for API access. To enable AI insights, "
            "please obtain a standard Anthropic API key from https://console.anthropic.com/"
        )
        return None
    
    try:
        return Anthropic(api_key=api_key)
    except Exception as e:
        st.error(f"⚠️ Failed to initialize Claude API client: {str(e)}")
        return None

def generate_executive_summary(metrics: Dict, revenue_df: pd.DataFrame) -> str:
    """Generate an AI-powered executive summary of current metrics.
    
    Args:
        metrics: Dictionary of current SaaS metrics
        revenue_df: DataFrame with historical revenue data
        
    Returns:
        AI-generated executive summary or helpful fallback message
    """
    client = get_claude_client()
    if not client:
        return (
            "💡 **AI Insights Unavailable**\n\n"
            "To enable AI-powered insights, configure a valid Anthropic API key. "
            "In the meantime, you can analyze your metrics using the charts and data tables above.\n\n"
            f"**Quick Summary**: Your MRR is ${metrics.get('mrr', 0):,.2f} with "
            f"{metrics.get('customers', 0):,} customers and a {metrics.get('churn_rate', 0):.1f}% churn rate."
        )
    
    # Prepare context for Claude
    context = f"""
Based on the following SaaS metrics, provide a brief executive summary (3-4 sentences):

Current Metrics:
- MRR: ${metrics.get('mrr', 0):,.2f} ({metrics.get('mrr_growth', 0):+.1f}% vs last month)
- Customers: {metrics.get('customers', 0):,} ({metrics.get('customer_growth', 0):+.1f}% growth)
- Churn Rate: {metrics.get('churn_rate', 0):.1f}%
- New Customers: {metrics.get('new_customers', 0)}

Recent Trend (last 3 months MRR):
{revenue_df.tail(3)[['month', 'mrr']].to_string(index=False) if not revenue_df.empty else 'No data'}

Focus on: overall health, key trends, and one actionable insight.
"""
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Latest Sonnet model
            max_tokens=300,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        return message.content[0].text
    except Exception as e:
        # Provide helpful fallback with error details
        error_msg = str(e)
        if "invalid x-api-key" in error_msg.lower() or "authentication" in error_msg.lower():
            return (
                "⚠️ **Authentication Error**: The API key is invalid or expired. "
                "Please check your Anthropic API key configuration.\n\n"
                f"**Quick Summary**: Your MRR is ${metrics.get('mrr', 0):,.2f} with "
                f"{metrics.get('customers', 0):,} customers."
            )
        return f"⚠️ Error generating AI summary: {error_msg}"

def answer_metric_question(question: str, metrics: Dict, revenue_df: pd.DataFrame, plan_df: pd.DataFrame) -> str:
    """Answer natural language questions about metrics using AI.
    
    Args:
        question: Natural language question about metrics
        metrics: Dictionary of current SaaS metrics
        revenue_df: DataFrame with historical revenue data
        plan_df: DataFrame with plan-level revenue data
        
    Returns:
        AI-generated answer or helpful fallback message
    """
    client = get_claude_client()
    if not client:
        return (
            "💡 **AI Insights Unavailable**\n\n"
            "To enable AI-powered Q&A, configure a valid Anthropic API key. "
            "You can still explore your metrics using the charts and data tables in the dashboard."
        )
    
    # Prepare data context
    context = f"""
You are a SaaS analytics assistant. Answer the user's question based on this data:

Current Metrics:
- MRR: ${metrics.get('mrr', 0):,.2f} (Growth: {metrics.get('mrr_growth', 0):+.1f}%)
- Customers: {metrics.get('customers', 0):,} (Growth: {metrics.get('customer_growth', 0):+.1f}%)
- Churn Rate: {metrics.get('churn_rate', 0):.1f}%
- New Customers This Month: {metrics.get('new_customers', 0)}

Monthly Revenue History:
{revenue_df[['month', 'mrr', 'customer_count']].tail(6).to_string(index=False) if not revenue_df.empty else 'No data'}

Revenue by Plan (latest month):
{plan_df.tail(3)[['plan_tier', 'revenue', 'customer_count']].to_string(index=False) if not plan_df.empty else 'No data'}

User Question: {question}

Provide a concise, actionable answer (2-3 sentences max).
"""
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Latest Sonnet model
            max_tokens=200,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        return message.content[0].text
    except Exception as e:
        error_msg = str(e)
        if "invalid x-api-key" in error_msg.lower() or "authentication" in error_msg.lower():
            return (
                "⚠️ **Authentication Error**: Unable to access AI insights. "
                "Please verify your Anthropic API key configuration."
            )
        return f"⚠️ Error generating answer: {error_msg}"
