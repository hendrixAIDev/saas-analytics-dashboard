# ⚡ Quick Start Guide

Get your SaaS Analytics Dashboard running in **5 minutes**.

## Prerequisites

✅ Python 3.11+  
✅ Supabase account (free)  
✅ Claude API key

## Setup Commands

```bash
# 1. Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Set up database
# - Go to supabase.com
# - Create new project
# - Run schema.sql in SQL Editor
# - Copy URL and Key to .env

# 4. Generate sample data
python seed_data.py

# 5. Launch dashboard
streamlit run app.py
```

## What You Need

### Supabase Setup (2 minutes)

1. Create account at [supabase.com](https://supabase.com)
2. New Project → Wait for setup
3. SQL Editor → Paste `schema.sql` → Run
4. Settings → API → Copy URL and anon key
5. Paste into `.env`

### Claude API Key (1 minute)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Get API key
3. Paste into `.env`

### .env File Format

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_long_anon_key_here
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## Verify It Works

1. ✅ Run `python seed_data.py` → See "✨ Database seeded successfully!"
2. ✅ Run `streamlit run app.py` → Browser opens
3. ✅ Sign up → Check email → Verify → Login
4. ✅ See dashboard with charts and metrics

## Common Issues

**"No module named 'streamlit'"**  
→ Activate your virtual environment

**"Supabase credentials not found"**  
→ Check `.env` file exists and has correct values

**"No data available"**  
→ Run `python seed_data.py`

**Email verification not arriving**  
→ Check spam folder, or use Supabase dashboard to confirm user manually

## Next Steps

Once running:
- Explore all 4 dashboard pages
- Try AI insights ("What's my biggest opportunity?")
- Check `CUSTOMIZATION.md` to personalize
- Read `README.md` for detailed docs

## Need Help?

1. Check `README.md` for detailed troubleshooting
2. Verify all prerequisites are installed
3. Make sure database tables are created
4. Check Supabase dashboard for any errors

---

**You're 5 minutes away from a beautiful SaaS dashboard! 🚀**
