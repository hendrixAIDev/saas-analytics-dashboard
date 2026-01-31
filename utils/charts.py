"""Chart generation utilities using Plotly."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional

def create_mrr_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create MRR trend line chart."""
    if df.empty:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['mrr'],
        mode='lines+markers',
        name='MRR',
        line=dict(color='#00C853', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(0, 200, 83, 0.1)'
    ))
    
    fig.update_layout(
        title='Monthly Recurring Revenue Trend',
        xaxis_title='Month',
        yaxis_title='MRR ($)',
        hovermode='x unified',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    
    return fig

def create_customer_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create customer count trend chart."""
    if df.empty:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['customer_count'],
        mode='lines+markers',
        name='Customers',
        line=dict(color='#2196F3', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Customer Growth',
        xaxis_title='Month',
        yaxis_title='Total Customers',
        hovermode='x unified',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    
    return fig

def create_churn_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create churn rate visualization."""
    if df.empty:
        return None
    
    # Calculate churn rate
    df['churn_rate'] = (df['churn_count'] / df['customer_count'] * 100).round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['month'],
        y=df['churn_rate'],
        name='Churn Rate',
        marker=dict(color='#FF5252')
    ))
    
    fig.update_layout(
        title='Monthly Churn Rate',
        xaxis_title='Month',
        yaxis_title='Churn Rate (%)',
        hovermode='x unified',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    
    return fig

def create_plan_revenue_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create revenue breakdown by plan tier."""
    if df.empty:
        return None
    
    # Get latest month data
    latest_month = df['month'].max()
    latest_data = df[df['month'] == latest_month]
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=latest_data['plan_tier'],
        values=latest_data['revenue'],
        hole=0.4,
        marker=dict(colors=['#00C853', '#2196F3', '#FF9800'])
    ))
    
    fig.update_layout(
        title='Revenue by Plan Tier (Current Month)',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0')
    )
    
    return fig

def create_cohort_retention_table(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Create cohort retention pivot table."""
    if df.empty:
        return None
    
    # Pivot the data
    pivot = df.pivot(
        index='cohort_month',
        columns='month_number',
        values='retention_rate'
    )
    
    # Format cohort_month as string
    pivot.index = pivot.index.strftime('%Y-%m')
    
    # Sort by cohort month descending
    pivot = pivot.sort_index(ascending=False)
    
    return pivot
