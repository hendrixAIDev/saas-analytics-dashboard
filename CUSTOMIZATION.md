# 🎨 Customization Guide

This guide shows you exactly where and how to customize the SaaS Analytics Dashboard to match your needs.

## 🎨 Styling & Branding

### Change Color Scheme

**File:** `assets/style.css`

```css
/* Primary color (green accent) */
Change #00C853 to your brand color

/* Background gradients */
background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
/* Change to your preferred gradient */

/* Sidebar background */
background: linear-gradient(180deg, #0f3460 0%, #16213e 100%);
```

**Quick color presets:**

```css
/* Blue theme */
#00C853 → #2196F3
#00E676 → #64B5F6

/* Purple theme */
#00C853 → #9C27B0
#00E676 → #BA68C8

/* Orange theme */
#00C853 → #FF9800
#00E676 → #FFB74D
```

### Change Logo/Title

**File:** `app.py`

```python
# Line 32-34 (Page config)
st.set_page_config(
    page_title="Your Company Dashboard",  # Browser tab title
    page_icon="🚀",  # Emoji or path to .ico file
    ...
)

# Line 55 (Login page)
st.title("🚀 Your Company Dashboard")

# Line 80 (Sidebar)
st.title("🚀 Your Dashboard")
```

### Customize Metric Labels

**File:** `app.py` → `show_overview_page()` function (around line 140)

```python
st.metric(
    "Monthly Recurring Revenue",  # ← Change this
    f"${metrics.get('mrr', 0):,.0f}",
    f"{metrics.get('mrr_growth', 0):+.1f}%"
)

# Example alternatives:
"Monthly Revenue" 
"ARR" (if tracking annually)
"Total Revenue"
```

## 📊 Adding New Metrics

### Step 1: Add to Database

**File:** `schema.sql`

```sql
-- Add new column to monthly_revenue table
ALTER TABLE monthly_revenue 
ADD COLUMN ltv DECIMAL(10, 2),
ADD COLUMN cac DECIMAL(10, 2);
```

### Step 2: Update Data Fetching

**File:** `utils/database.py`

```python
def get_current_metrics(supabase: Client) -> Dict:
    # Add your new metrics to the return dict
    return {
        'mrr': current['mrr'],
        'ltv': current['ltv'],  # ← Add this
        'cac': current['cac'],  # ← Add this
        ...
    }
```

### Step 3: Display on Dashboard

**File:** `app.py` → `show_overview_page()`

```python
# Add a new column
col5 = st.columns(5)  # Change from 4 to 5

with col5:
    st.metric(
        "Customer LTV",
        f"${metrics.get('ltv', 0):,.0f}"
    )
```

### Step 4: Update Seed Data

**File:** `seed_data.py` → `generate_monthly_data()`

```python
data.append({
    'month': month_date.strftime('%Y-%m-01'),
    'mrr': round(mrr, 2),
    'ltv': round(mrr / customers * 12, 2),  # ← Add calculation
    ...
})
```

## 📈 Adding New Charts

### Create Chart Function

**File:** `utils/charts.py`

```python
def create_ltv_cac_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create LTV vs CAC comparison chart."""
    if df.empty:
        return None
    
    fig = go.Figure()
    
    # Add LTV line
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['ltv'],
        mode='lines+markers',
        name='LTV',
        line=dict(color='#00C853', width=3)
    ))
    
    # Add CAC line
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['cac'],
        mode='lines+markers',
        name='CAC',
        line=dict(color='#FF5252', width=3)
    ))
    
    fig.update_layout(
        title='LTV vs CAC Trend',
        xaxis_title='Month',
        yaxis_title='Value ($)',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0')
    )
    
    return fig
```

### Display Chart on Dashboard

**File:** `app.py`

```python
# Import your new chart function
from utils.charts import create_ltv_cac_chart

# Add to your page function
def show_overview_page(...):
    ...
    ltv_cac_chart = create_ltv_cac_chart(revenue_df)
    if ltv_cac_chart:
        st.plotly_chart(ltv_cac_chart, use_container_width=True)
```

## 🤖 Customizing AI Insights

### Modify Executive Summary Prompt

**File:** `utils/ai_insights.py` → `generate_executive_summary()`

```python
context = f"""
Based on the following SaaS metrics, provide a brief executive summary:

{your_custom_context_here}

Focus on: {your_custom_instructions}
"""
```

### Change AI Model

**File:** `utils/ai_insights.py`

```python
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",  # ← Change model here
    # Options: "claude-3-opus-20240229", "claude-3-sonnet-20240229"
    max_tokens=300,
    ...
)
```

### Add New AI Features

Example: Monthly recommendations

```python
def generate_monthly_recommendations(metrics: Dict) -> str:
    """Generate AI-powered action recommendations."""
    client = get_claude_client()
    if not client:
        return "AI unavailable"
    
    context = f"""
    Based on these SaaS metrics, provide 3 specific action items:
    
    MRR: ${metrics['mrr']:,.2f}
    Churn: {metrics['churn_rate']:.1f}%
    Growth: {metrics['customer_growth']:+.1f}%
    
    Format as a numbered list.
    """
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=250,
        messages=[{"role": "user", "content": context}]
    )
    
    return message.content[0].text
```

## 📱 Adding New Pages

### Step 1: Create Page Function

**File:** `app.py`

```python
def show_forecasting_page(revenue_df: pd.DataFrame):
    """Display revenue forecasting page."""
    st.title("🔮 Revenue Forecasting")
    
    st.subheader("6-Month Projection")
    # Your forecasting logic here
    
    st.markdown("---")
    # Add charts, metrics, etc.
```

### Step 2: Add to Navigation

**File:** `app.py` → `show_dashboard()`

```python
# Add to navigation radio
page = st.radio(
    "Navigation",
    ["Overview", "Revenue Analytics", "Customer Insights", 
     "AI Insights", "Forecasting"],  # ← Add here
    ...
)

# Add to page routing
elif page == "Forecasting":
    show_forecasting_page(revenue_df)
```

## 🔧 Configuration Options

### Change Time Range

**File:** `app.py`

```python
# Change from 12 months to 6 months
revenue_df = get_monthly_revenue(supabase, months=6)  # ← Change here

# Or add user control
months = st.sidebar.slider("Time Range (months)", 3, 24, 12)
revenue_df = get_monthly_revenue(supabase, months=months)
```

### Modify Plan Tiers

**File:** `seed_data.py`

```python
# Change plan names and prices
PLAN_PRICES = {
    'basic': 19,      # ← Rename/reprice
    'premium': 49,
    'ultimate': 199
}

# Update distribution
starter_customers = int(total_customers * 0.60)  # ← Adjust percentages
pro_customers = int(total_customers * 0.30)
```

**Don't forget to update:**
- `schema.sql` (plan_tier constraints if using enums)
- `app.py` (display labels)

## 🎯 Advanced Customizations

### Add Multi-Tenancy

**File:** `utils/database.py`

```python
def get_monthly_revenue(supabase: Client, user_id: str, months: int = 12):
    """Fetch revenue data for specific user."""
    response = supabase.table("monthly_revenue")\
        .select("*")\
        .eq("user_id", user_id)\  # ← Add user filter
        .order("month", desc=True)\
        .limit(months)\
        .execute()
    ...
```

### Add Data Export

**File:** `app.py`

```python
import io

def export_to_csv(df: pd.DataFrame, filename: str):
    """Export dataframe to downloadable CSV."""
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

# Use in your page:
export_to_csv(revenue_df, "revenue_data.csv")
```

### Add Real-Time Updates

**File:** `app.py`

```python
import time

# Add auto-refresh
if st.sidebar.checkbox("Auto-refresh (30s)"):
    time.sleep(30)
    st.rerun()
```

## 🔍 Debugging Tips

### Enable Debug Mode

**File:** `app.py`

```python
# Add to sidebar
if st.sidebar.checkbox("Debug Mode"):
    st.sidebar.json(st.session_state.to_dict())
    st.sidebar.write("Current metrics:", metrics)
    st.sidebar.write("DataFrame shape:", revenue_df.shape)
```

### Test with Sample Data

```python
# Create test data without database
if st.sidebar.button("Use Test Data"):
    revenue_df = pd.DataFrame({
        'month': pd.date_range('2023-01-01', periods=12, freq='MS'),
        'mrr': [5000 + i*500 for i in range(12)],
        'customer_count': [50 + i*5 for i in range(12)]
    })
```

## 📦 Before You Deploy

### Checklist

- [ ] Remove debug code
- [ ] Update `.env.example` with all required variables
- [ ] Test with fresh database
- [ ] Run `python seed_data.py` to verify seed script works
- [ ] Test authentication flow (signup → verify → login)
- [ ] Check mobile responsiveness
- [ ] Verify all charts render correctly
- [ ] Test AI insights with various questions
- [ ] Update README with your customizations

### Environment Variables for Production

```bash
# .env for production
SUPABASE_URL=your_prod_url
SUPABASE_KEY=your_prod_key
ANTHROPIC_API_KEY=your_api_key

# Optional: Add these
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=warning
```

---

## 🎓 Learning Resources

**Streamlit:**
- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Gallery](https://streamlit.io/gallery)

**Plotly:**
- [Plotly Python](https://plotly.com/python/)
- [Chart Examples](https://plotly.com/python/basic-charts/)

**Supabase:**
- [Supabase Docs](https://supabase.com/docs)
- [Python Client](https://supabase.com/docs/reference/python)

**Claude API:**
- [Anthropic Docs](https://docs.anthropic.com)

---

**Happy customizing! 🚀**

If you build something cool, share it with the community!
