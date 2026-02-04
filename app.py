"""
SaaS Analytics Dashboard
A production-ready Streamlit template for SaaS metrics visualization
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

# Import custom utilities
from utils.auth import login, signup, logout, check_authentication, get_supabase_client
from utils.database import (
    get_monthly_revenue,
    get_revenue_by_plan,
    get_cohort_retention,
    get_current_metrics
)
from utils.charts import (
    create_mrr_chart,
    create_customer_chart,
    create_churn_chart,
    create_plan_revenue_chart,
    create_cohort_retention_table
)
from utils.ai_insights import generate_executive_summary, answer_metric_question

# Page configuration
st.set_page_config(
    page_title="SaaS Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = Path(__file__).parent / "assets" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'just_signed_up' not in st.session_state:
    st.session_state.just_signed_up = False

def show_login_page():
    """Display login/signup page."""
    st.title("📊 SaaS Analytics Dashboard")
    st.markdown("### Welcome! Please login to continue.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if email and password:
                    if login(email, password):
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.warning("Please enter both email and password")
    
    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
            submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit:
                if email and password and password_confirm:
                    if password == password_confirm:
                        if len(password) >= 6:
                            if signup(email, password):
                                # Mark that we just signed up (for welcome message on dashboard)
                                if st.session_state.authenticated:
                                    st.session_state.just_signed_up = True
                                st.rerun()
                        else:
                            st.error("Password must be at least 6 characters")
                    else:
                        st.error("Passwords don't match")
                else:
                    st.warning("Please fill in all fields")

def show_dashboard():
    """Display main dashboard."""
    # Show welcome message for new signups
    if st.session_state.get('just_signed_up', False):
        st.success("✅ Account created! You're now logged in.")
        st.balloons()  # Celebratory effect for new users
        st.session_state.just_signed_up = False  # Clear the flag
    
    # Sidebar
    with st.sidebar:
        st.title("📊 Dashboard")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["Overview", "Revenue Analytics", "Customer Insights", "AI Insights"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # User info
        if st.session_state.user:
            st.markdown(f"**User:** {st.session_state.user.email}")
        
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    # Fetch data
    revenue_df = get_monthly_revenue(supabase, months=12)
    plan_df = get_revenue_by_plan(supabase, months=12)
    cohort_df = get_cohort_retention(supabase, cohorts=6)
    current_metrics = get_current_metrics(supabase)
    
    # Show selected page
    if page == "Overview":
        show_overview_page(current_metrics, revenue_df, plan_df)
    elif page == "Revenue Analytics":
        show_revenue_page(revenue_df, plan_df)
    elif page == "Customer Insights":
        show_customer_page(revenue_df, cohort_df)
    elif page == "AI Insights":
        show_ai_insights_page(current_metrics, revenue_df, plan_df)

def show_overview_page(metrics: dict, revenue_df: pd.DataFrame, plan_df: pd.DataFrame):
    """Display overview page with key metrics."""
    st.title("📈 Dashboard Overview")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    if not metrics:
        st.warning("⚠️ No data available. Please run the seed script to populate sample data.")
        st.code("python seed_data.py", language="bash")
        return
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Monthly Recurring Revenue",
            f"${metrics.get('mrr', 0):,.0f}",
            f"{metrics.get('mrr_growth', 0):+.1f}%"
        )
    
    with col2:
        st.metric(
            "Total Customers",
            f"{metrics.get('customers', 0):,}",
            f"{metrics.get('customer_growth', 0):+.1f}%"
        )
    
    with col3:
        st.metric(
            "Churn Rate",
            f"{metrics.get('churn_rate', 0):.1f}%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "New Customers",
            f"{metrics.get('new_customers', 0):,}"
        )
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        mrr_chart = create_mrr_chart(revenue_df)
        if mrr_chart:
            st.plotly_chart(mrr_chart, use_container_width=True)
    
    with col2:
        customer_chart = create_customer_chart(revenue_df)
        if customer_chart:
            st.plotly_chart(customer_chart, use_container_width=True)

def show_revenue_page(revenue_df: pd.DataFrame, plan_df: pd.DataFrame):
    """Display revenue analytics page."""
    st.title("💰 Revenue Analytics")
    
    if revenue_df.empty:
        st.warning("⚠️ No revenue data available.")
        return
    
    # MRR trend
    st.subheader("MRR Trend")
    mrr_chart = create_mrr_chart(revenue_df)
    if mrr_chart:
        st.plotly_chart(mrr_chart, use_container_width=True)
    
    st.markdown("---")
    
    # Revenue breakdown
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Revenue by Plan Tier")
        plan_chart = create_plan_revenue_chart(plan_df)
        if plan_chart:
            st.plotly_chart(plan_chart, use_container_width=True)
    
    with col2:
        st.subheader("Plan Breakdown Table")
        if not plan_df.empty:
            latest_month = plan_df['month'].max()
            latest_plan_data = plan_df[plan_df['month'] == latest_month][['plan_tier', 'revenue', 'customer_count']]
            latest_plan_data.columns = ['Plan', 'Revenue', 'Customers']
            latest_plan_data['Revenue'] = latest_plan_data['Revenue'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(latest_plan_data, use_container_width=True, hide_index=True)

def show_customer_page(revenue_df: pd.DataFrame, cohort_df: pd.DataFrame):
    """Display customer insights page."""
    st.title("👥 Customer Insights")
    
    # Customer growth chart
    st.subheader("Customer Growth")
    customer_chart = create_customer_chart(revenue_df)
    if customer_chart:
        st.plotly_chart(customer_chart, use_container_width=True)
    
    st.markdown("---")
    
    # Churn analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Churn Rate Analysis")
        churn_chart = create_churn_chart(revenue_df)
        if churn_chart:
            st.plotly_chart(churn_chart, use_container_width=True)
    
    with col2:
        st.subheader("Recent Trends")
        if not revenue_df.empty:
            recent = revenue_df.tail(3)[['month', 'new_customers', 'churn_count']].copy()
            recent['month'] = recent['month'].dt.strftime('%Y-%m')
            recent.columns = ['Month', 'New', 'Churned']
            st.dataframe(recent, use_container_width=True, hide_index=True)
    
    # Cohort retention
    st.markdown("---")
    st.subheader("Cohort Retention Analysis")
    
    if not cohort_df.empty:
        cohort_table = create_cohort_retention_table(cohort_df)
        if cohort_table is not None:
            # Style the dataframe
            styled_table = cohort_table.style.format("{:.1f}%")\
                .background_gradient(cmap='RdYlGn', vmin=0, vmax=100)
            st.dataframe(styled_table, use_container_width=True)
            st.caption("Retention rates by cohort month (rows) and months since signup (columns)")
    else:
        st.info("No cohort data available yet.")

def show_ai_insights_page(metrics: dict, revenue_df: pd.DataFrame, plan_df: pd.DataFrame):
    """Display AI-powered insights page."""
    st.title("🤖 AI-Powered Insights")
    
    if not metrics:
        st.warning("⚠️ No data available for AI analysis.")
        return
    
    # Executive Summary
    st.subheader("📋 Executive Summary")
    with st.spinner("Generating AI summary..."):
        summary = generate_executive_summary(metrics, revenue_df)
        st.info(summary)
    
    st.markdown("---")
    
    # Ask about your metrics
    st.subheader("💬 Ask About Your Metrics")
    st.markdown("Ask me anything about your SaaS metrics in natural language!")
    
    # Sample questions
    with st.expander("📌 Sample Questions"):
        st.markdown("""
        - What's driving my revenue growth?
        - How is my churn rate trending?
        - Which plan tier is most profitable?
        - Should I be worried about customer growth?
        - What should I focus on this month?
        """)
    
    question = st.text_input("Your question:", placeholder="e.g., What's my biggest growth opportunity?")
    
    if st.button("Get AI Insight", type="primary"):
        if question:
            with st.spinner("Analyzing your data..."):
                answer = answer_metric_question(question, metrics, revenue_df, plan_df)
                st.success(answer)
        else:
            st.warning("Please enter a question")

# Main app logic
def main():
    if check_authentication():
        show_dashboard()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
