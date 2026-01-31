"""Database query utilities."""
import pandas as pd
from supabase import Client
from datetime import datetime, timedelta
from typing import Dict, List
import streamlit as st

def get_monthly_revenue(supabase: Client, months: int = 12) -> pd.DataFrame:
    """Fetch monthly revenue data."""
    try:
        response = supabase.table("monthly_revenue")\
            .select("*")\
            .order("month", desc=True)\
            .limit(months)\
            .execute()
        
        df = pd.DataFrame(response.data)
        if not df.empty:
            df['month'] = pd.to_datetime(df['month'])
            df = df.sort_values('month')
        return df
    except Exception as e:
        st.error(f"Error fetching revenue data: {str(e)}")
        return pd.DataFrame()

def get_revenue_by_plan(supabase: Client, months: int = 12) -> pd.DataFrame:
    """Fetch revenue breakdown by plan tier."""
    try:
        response = supabase.table("revenue_by_plan")\
            .select("*")\
            .order("month", desc=True)\
            .limit(months * 3)\
            .execute()
        
        df = pd.DataFrame(response.data)
        if not df.empty:
            df['month'] = pd.to_datetime(df['month'])
            df = df.sort_values(['month', 'plan_tier'])
        return df
    except Exception as e:
        st.error(f"Error fetching plan data: {str(e)}")
        return pd.DataFrame()

def get_cohort_retention(supabase: Client, cohorts: int = 6) -> pd.DataFrame:
    """Fetch cohort retention data."""
    try:
        response = supabase.table("cohort_retention")\
            .select("*")\
            .order("cohort_month", desc=True)\
            .execute()
        
        df = pd.DataFrame(response.data)
        if not df.empty:
            df['cohort_month'] = pd.to_datetime(df['cohort_month'])
            # Filter to recent cohorts
            recent_cohorts = df['cohort_month'].unique()[:cohorts]
            df = df[df['cohort_month'].isin(recent_cohorts)]
            df = df.sort_values(['cohort_month', 'month_number'])
        return df
    except Exception as e:
        st.error(f"Error fetching cohort data: {str(e)}")
        return pd.DataFrame()

def get_current_metrics(supabase: Client) -> Dict:
    """Get current month's key metrics."""
    try:
        # Get latest month's data
        response = supabase.table("monthly_revenue")\
            .select("*")\
            .order("month", desc=True)\
            .limit(2)\
            .execute()
        
        data = response.data
        if len(data) < 1:
            return {}
        
        current = data[0]
        previous = data[1] if len(data) > 1 else current
        
        # Calculate growth rates
        mrr_growth = ((current['mrr'] - previous['mrr']) / previous['mrr'] * 100) if previous['mrr'] > 0 else 0
        customer_growth = ((current['customer_count'] - previous['customer_count']) / previous['customer_count'] * 100) if previous['customer_count'] > 0 else 0
        churn_rate = (current['churn_count'] / current['customer_count'] * 100) if current['customer_count'] > 0 else 0
        
        return {
            'mrr': current['mrr'],
            'mrr_growth': mrr_growth,
            'customers': current['customer_count'],
            'customer_growth': customer_growth,
            'churn_rate': churn_rate,
            'new_customers': current['new_customers']
        }
    except Exception as e:
        st.error(f"Error fetching current metrics: {str(e)}")
        return {}

def execute_query(supabase: Client, query: str) -> pd.DataFrame:
    """Execute a custom SQL query (for AI insights)."""
    try:
        # Note: Supabase client doesn't support raw SQL directly
        # This is a placeholder - in production, you'd use PostgREST or a direct connection
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return pd.DataFrame()
