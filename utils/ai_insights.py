"""AI-powered insights using Claude API."""
import os
from anthropic import Anthropic
import streamlit as st
from typing import Dict
import pandas as pd

def get_claude_client():
    """Initialize Claude API client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ Claude API key not found. Please check your .env file.")
        return None
    return Anthropic(api_key=api_key)

def generate_executive_summary(metrics: Dict, revenue_df: pd.DataFrame) -> str:
    """Generate an AI-powered executive summary of current metrics."""
    client = get_claude_client()
    if not client:
        return "AI insights unavailable. Please configure your Claude API key."
    
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
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def answer_metric_question(question: str, metrics: Dict, revenue_df: pd.DataFrame, plan_df: pd.DataFrame) -> str:
    """Answer natural language questions about metrics using AI."""
    client = get_claude_client()
    if not client:
        return "AI insights unavailable. Please configure your Claude API key."
    
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
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"
