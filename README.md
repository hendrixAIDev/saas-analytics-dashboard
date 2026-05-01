# 📊 SaaS Analytics Dashboard

A production-ready Streamlit dashboard template for SaaS metrics visualization. Perfect for indie hackers, startup founders, and SaaS businesses who need beautiful analytics without the complexity.

![Dashboard Preview](https://via.placeholder.com/800x400/1a1a2e/00C853?text=SaaS+Analytics+Dashboard)

## ✨ Features

- **📈 Key SaaS Metrics**: MRR, customer count, churn rate, growth trends
- **🎨 Beautiful UI**: Custom dark theme with professional styling
- **🔐 Supabase Auth**: Secure login/signup with email+password
- **🤖 AI Insights**: Powered by Claude API for natural language metric queries
- **📊 Rich Visualizations**: Interactive charts with Plotly
- **💾 PostgreSQL Database**: Robust data storage with Supabase
- **📱 Responsive Design**: Works on desktop and mobile
- **🚀 Easy Setup**: Running in under 5 minutes

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Python 3.11 or higher
- A Supabase account (free tier works!)
- Claude API key (from Anthropic)

### Step 1: Clone & Install

```bash
# Navigate to the project directory
cd saas-analytics-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Once created, go to **SQL Editor** and run the contents of `schema.sql`
3. Get your credentials from **Settings → API**:
   - Project URL
   - Anon/Public key

### Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your credentials:
# - SUPABASE_URL=your_project_url
# - SUPABASE_KEY=your_anon_key
# - ANTHROPIC_API_KEY=your_claude_api_key
```

### Step 4: Seed Sample Data

```bash
# Generate 12 months of realistic sample data
python seed_data.py
```

### Step 5: Launch Dashboard

```bash
streamlit run app.py
```

Visit `http://localhost:8501` and you're live! 🎉

## 📖 Usage

### Creating Your First User

1. Click the "Sign Up" tab
2. Enter email and password (minimum 6 characters)
3. Check your email for verification link
4. Login with your credentials

### Navigating the Dashboard

- **Overview**: High-level metrics and trends
- **Revenue Analytics**: Deep dive into MRR and plan breakdowns
- **Customer Insights**: Growth, churn, and cohort retention
- **AI Insights**: Ask questions about your metrics in natural language

### Sample AI Questions

Try asking:
- "What's driving my revenue growth?"
- "How is my churn rate trending?"
- "Which plan tier is most profitable?"
- "Should I be worried about customer growth?"

## 🗂️ Project Structure

```
saas-analytics-dashboard/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── schema.sql             # Database schema
├── seed_data.py           # Sample data generator
├── README.md              # This file
├── CUSTOMIZATION.md       # Customization guide
├── utils/
│   ├── auth.py           # Supabase authentication
│   ├── database.py       # Database queries
│   ├── ai_insights.py    # Claude API integration
│   └── charts.py         # Plotly chart generation
└── assets/
    └── style.css         # Custom CSS theme
```

## 🔧 Customization

See [CUSTOMIZATION.md](CUSTOMIZATION.md) for detailed instructions on:
- Changing colors and styling
- Adding new metrics
- Modifying database schema
- Customizing AI prompts
- Adding new chart types

## 💡 Common Use Cases

### For Indie Hackers
Track your SaaS metrics without expensive tools like ChartMogul or Baremetrics. Perfect for validating product-market fit.

### For Startup Founders
Share beautiful metrics with investors and team members. Export charts for pitch decks.

### For Agencies
White-label template for client dashboards. Customize branding and metrics per client.

## 🛠️ Tech Stack

- **Frontend**: Streamlit 1.31
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Charts**: Plotly 5.18
- **AI**: Anthropic Claude API
- **Data**: Pandas, NumPy

## 📊 Metrics Tracked

| Metric | Description |
|--------|-------------|
| **MRR** | Monthly Recurring Revenue with growth trends |
| **Customer Count** | Total active customers with growth rate |
| **Churn Rate** | Percentage of customers lost each month |
| **Plan Breakdown** | Revenue and customers by tier (Starter/Pro/Enterprise) |
| **Cohort Retention** | Customer retention by signup month |
| **New Customers** | Monthly customer acquisition |

## 🔒 Security Notes

- Never commit your `.env` file to git
- Use environment variables for all secrets
- Supabase handles authentication securely
- Row-level security can be added in Supabase for multi-tenancy

## 📝 License

This template is provided as-is for personal and commercial use.

## 🆘 Support

**Issues?** Check these common solutions:

### "No data available"
→ Run `python seed_data.py` to generate sample data

### "Supabase credentials not found"
→ Make sure `.env` file exists with valid credentials

### "Login failed"
→ Check your email for verification link from Supabase

### Charts not displaying
→ Ensure you have data in the database and tables are created

## 🚀 What's Next?

Once you're comfortable with the template:

1. **Connect Real Data**: Replace sample data with your actual SaaS metrics
2. **Add More Metrics**: LTV, CAC, runway, burn rate, etc.
3. **Customize Styling**: Match your brand colors
4. **Deploy**: Use Streamlit Cloud, Heroku, or DigitalOcean
5. **Add Features**: Email reports, Slack notifications, export to CSV

## 💰 Worth $49?

This template saves you:
- **$299/mo** - ChartMogul subscription
- **40+ hours** - Building from scratch
- **$2000+** - Hiring a developer

All for a one-time purchase. You get:
- ✅ Production-ready code
- ✅ Beautiful UI/UX
- ✅ AI-powered insights
- ✅ Full customization rights
- ✅ No ongoing fees

---

**Built with ❤️ for the indie maker community**

Questions? Found a bug? Want to share your customization?  
Open an issue or submit a PR!
