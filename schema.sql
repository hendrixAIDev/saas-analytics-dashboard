-- SaaS Analytics Dashboard Database Schema

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    signup_date DATE NOT NULL,
    plan_tier VARCHAR(50) NOT NULL, -- 'starter', 'pro', 'enterprise'
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- 'active', 'churned'
    churn_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Monthly revenue records
CREATE TABLE IF NOT EXISTS monthly_revenue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    month DATE NOT NULL,
    mrr DECIMAL(10, 2) NOT NULL,
    customer_count INTEGER NOT NULL,
    churn_count INTEGER DEFAULT 0,
    new_customers INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    UNIQUE(month)
);

-- Revenue by plan tier
CREATE TABLE IF NOT EXISTS revenue_by_plan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    month DATE NOT NULL,
    plan_tier VARCHAR(50) NOT NULL,
    revenue DECIMAL(10, 2) NOT NULL,
    customer_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    UNIQUE(month, plan_tier)
);

-- Cohort retention data
CREATE TABLE IF NOT EXISTS cohort_retention (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_month DATE NOT NULL,
    month_number INTEGER NOT NULL, -- 0 = signup month, 1 = 1 month later, etc.
    customers_remaining INTEGER NOT NULL,
    retention_rate DECIMAL(5, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    UNIQUE(cohort_month, month_number)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_customers_signup_date ON customers(signup_date);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_monthly_revenue_month ON monthly_revenue(month);
CREATE INDEX IF NOT EXISTS idx_revenue_by_plan_month ON revenue_by_plan(month);
CREATE INDEX IF NOT EXISTS idx_cohort_retention_cohort_month ON cohort_retention(cohort_month);
