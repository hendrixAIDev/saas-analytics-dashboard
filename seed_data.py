"""
Seed script to populate database with realistic SaaS sample data.
Run this script after setting up your Supabase database and .env file.
"""

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
import numpy as np
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Plan pricing
PLAN_PRICES = {
    'starter': 29,
    'pro': 99,
    'enterprise': 299
}

def get_supabase_client():
    """Initialize Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Missing Supabase credentials. Check your .env file.")
    
    return create_client(url, key)

def generate_monthly_data(months=12):
    """Generate realistic monthly revenue data."""
    data = []
    base_customers = 50
    base_mrr = 5000
    
    # Start date (12 months ago)
    start_date = datetime.now() - relativedelta(months=months-1)
    
    for i in range(months):
        month_date = start_date + relativedelta(months=i)
        
        # Growth with some randomness
        growth_factor = 1 + (i * 0.08) + random.uniform(-0.05, 0.1)
        customers = int(base_customers * growth_factor)
        
        # MRR calculation with variance
        mrr = base_mrr * growth_factor * random.uniform(0.95, 1.05)
        
        # Churn increases slightly with size
        churn_rate = min(0.05 + (i * 0.002), 0.08)
        churn_count = int(customers * churn_rate * random.uniform(0.8, 1.2))
        
        # New customers = growth + churn replacement
        if i > 0:
            prev_customers = data[i-1]['customer_count']
            new_customers = max(customers - prev_customers + churn_count, 0)
        else:
            new_customers = int(customers * 0.15)
        
        data.append({
            'month': month_date.strftime('%Y-%m-01'),
            'mrr': round(mrr, 2),
            'customer_count': customers,
            'churn_count': churn_count,
            'new_customers': new_customers
        })
    
    return data

def generate_plan_data(monthly_data):
    """Generate revenue breakdown by plan tier."""
    plan_data = []
    
    for month_data in monthly_data:
        total_customers = month_data['customer_count']
        total_mrr = month_data['mrr']
        
        # Distribution: 50% starter, 35% pro, 15% enterprise
        starter_customers = int(total_customers * 0.50)
        pro_customers = int(total_customers * 0.35)
        enterprise_customers = total_customers - starter_customers - pro_customers
        
        # Calculate revenue (with some variance from ideal)
        starter_revenue = starter_customers * PLAN_PRICES['starter'] * random.uniform(0.95, 1.05)
        pro_revenue = pro_customers * PLAN_PRICES['pro'] * random.uniform(0.95, 1.05)
        enterprise_revenue = enterprise_customers * PLAN_PRICES['enterprise'] * random.uniform(0.95, 1.05)
        
        # Normalize to match total MRR
        total_calc = starter_revenue + pro_revenue + enterprise_revenue
        if total_calc > 0:
            ratio = total_mrr / total_calc
            starter_revenue *= ratio
            pro_revenue *= ratio
            enterprise_revenue *= ratio
        
        plan_data.extend([
            {
                'month': month_data['month'],
                'plan_tier': 'starter',
                'revenue': round(starter_revenue, 2),
                'customer_count': starter_customers
            },
            {
                'month': month_data['month'],
                'plan_tier': 'pro',
                'revenue': round(pro_revenue, 2),
                'customer_count': pro_customers
            },
            {
                'month': month_data['month'],
                'plan_tier': 'enterprise',
                'revenue': round(enterprise_revenue, 2),
                'customer_count': enterprise_customers
            }
        ])
    
    return plan_data

def generate_cohort_data(months=6):
    """Generate cohort retention data."""
    cohort_data = []
    
    # Start 6 months ago for cohorts
    start_date = datetime.now() - relativedelta(months=months-1)
    
    for cohort_idx in range(months):
        cohort_month = start_date + relativedelta(months=cohort_idx)
        cohort_month_str = cohort_month.strftime('%Y-%m-01')
        
        # Initial cohort size
        initial_customers = random.randint(20, 50)
        
        # Generate retention for up to 6 months
        max_months = min(6, months - cohort_idx)
        
        for month_num in range(max_months):
            # Retention curve: starts high, decreases over time
            # Month 0: 100%, Month 1: ~85%, Month 2: ~75%, etc.
            base_retention = 100 - (month_num * 8) - random.uniform(0, 5)
            base_retention = max(base_retention, 60)  # Floor at 60%
            
            customers_remaining = int(initial_customers * (base_retention / 100))
            
            cohort_data.append({
                'cohort_month': cohort_month_str,
                'month_number': month_num,
                'customers_remaining': customers_remaining,
                'retention_rate': round(base_retention, 2)
            })
    
    return cohort_data

def seed_database():
    """Main function to seed the database."""
    print("🌱 Starting database seeding...")
    
    try:
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Generate data
        print("\n📊 Generating sample data...")
        monthly_data = generate_monthly_data(months=12)
        plan_data = generate_plan_data(monthly_data)
        cohort_data = generate_cohort_data(months=6)
        
        print(f"  - {len(monthly_data)} monthly revenue records")
        print(f"  - {len(plan_data)} plan breakdown records")
        print(f"  - {len(cohort_data)} cohort retention records")
        
        # Clear existing data
        print("\n🧹 Clearing existing data...")
        supabase.table("monthly_revenue").delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table("revenue_by_plan").delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table("cohort_retention").delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        # Insert new data
        print("\n💾 Inserting data...")
        
        print("  - Monthly revenue...")
        supabase.table("monthly_revenue").insert(monthly_data).execute()
        
        print("  - Revenue by plan...")
        supabase.table("revenue_by_plan").insert(plan_data).execute()
        
        print("  - Cohort retention...")
        supabase.table("cohort_retention").insert(cohort_data).execute()
        
        print("\n✨ Database seeded successfully!")
        print("\n📈 Sample metrics from latest month:")
        latest = monthly_data[-1]
        print(f"  - MRR: ${latest['mrr']:,.2f}")
        print(f"  - Customers: {latest['customer_count']:,}")
        print(f"  - New Customers: {latest['new_customers']}")
        print(f"  - Churn: {latest['churn_count']}")
        print("\n🚀 Ready to run: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("  1. Created the database tables (run schema.sql in Supabase)")
        print("  2. Set up your .env file with SUPABASE_URL and SUPABASE_KEY")
        return False
    
    return True

if __name__ == "__main__":
    seed_database()
