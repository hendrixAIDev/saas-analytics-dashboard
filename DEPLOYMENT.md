# 🚀 Deployment Guide

This guide shows you how to deploy your SaaS Analytics Dashboard to production.

## Deployment Options

### Option 1: Streamlit Community Cloud (Recommended - Free)

**Best for:** Personal use, demos, small teams

1. **Push to GitHub**
```bash
# Create GitHub repo
gh repo create saas-analytics-dashboard --public --source=. --remote=origin

# Push code
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repo
   - Main file path: `app.py`
   - Add secrets in "Advanced settings":
     ```toml
     SUPABASE_URL = "your_url"
     SUPABASE_KEY = "your_key"
     ANTHROPIC_API_KEY = "your_key"
     ```
   - Click "Deploy"

3. **Run seed script**
   - After deployment, run seed_data.py locally to populate database
   - Or use Supabase SQL editor directly

**URL:** `https://your-app.streamlit.app`  
**Cost:** Free  
**Limitations:** Community tier (limited resources)

---

### Option 2: Heroku

**Best for:** Production apps, custom domains

1. **Install Heroku CLI**
```bash
brew install heroku/brew/heroku  # macOS
```

2. **Create Heroku app**
```bash
heroku create your-dashboard-name
```

3. **Add buildpack**
```bash
heroku buildpacks:set heroku/python
```

4. **Create Procfile**
```bash
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

5. **Set environment variables**
```bash
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_KEY=your_key
heroku config:set ANTHROPIC_API_KEY=your_key
```

6. **Deploy**
```bash
git push heroku main
```

**Cost:** $7/month (Eco Dyno)  
**Custom domain:** Available

---

### Option 3: DigitalOcean App Platform

**Best for:** Scalable production apps

1. **Create App**
   - Go to DigitalOcean App Platform
   - Connect GitHub repo
   - Select repo and branch

2. **Configure**
   - Build command: `pip install -r requirements.txt`
   - Run command: `streamlit run app.py --server.port=8080 --server.address=0.0.0.0`

3. **Add Environment Variables**
   ```
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   ANTHROPIC_API_KEY=your_key
   ```

4. **Deploy**

**Cost:** $5/month (Basic plan)  
**Auto-scaling:** Available

---

### Option 4: Docker + Any Cloud Provider

**Best for:** Maximum control, enterprise deployments

1. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
```

3. **Build and run**
```bash
docker-compose up -d
```

4. **Deploy to any cloud**
   - AWS ECS
   - Google Cloud Run
   - Azure Container Instances
   - DigitalOcean Droplet

**Cost:** Varies by provider  
**Control:** Maximum

---

## Pre-Deployment Checklist

### Code
- [ ] Remove debug statements
- [ ] Update `.env.example` with all variables
- [ ] Test with fresh install
- [ ] Run all features manually
- [ ] Check error handling

### Database
- [ ] Run `schema.sql` in production Supabase
- [ ] Enable Row Level Security (if needed)
- [ ] Set up backups
- [ ] Test connection from deployed app

### Environment Variables
- [ ] All keys in deployment platform
- [ ] No secrets in code
- [ ] Test environment variable loading

### Security
- [ ] HTTPS enabled
- [ ] Environment variables secure
- [ ] No exposed secrets in logs
- [ ] Supabase RLS configured (if needed)

### Performance
- [ ] Test with production data volume
- [ ] Optimize large queries
- [ ] Add caching where needed
- [ ] Test load time

### Documentation
- [ ] Update README with deployed URL
- [ ] Document deployment steps taken
- [ ] Create runbook for common issues

---

## Post-Deployment

### Monitor
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Check error logs regularly
- [ ] Monitor API usage (Claude, Supabase)
- [ ] Track user signups

### Backups
- [ ] Enable Supabase daily backups
- [ ] Export database weekly
- [ ] Version control all code changes

### Updates
- [ ] Create staging environment
- [ ] Test updates before production
- [ ] Keep dependencies updated
- [ ] Monitor security advisories

---

## Custom Domain Setup

### Streamlit Cloud
1. Get domain (Namecheap, Google Domains)
2. Add CNAME record: `dashboard.yourdomain.com` → `your-app.streamlit.app`
3. Contact Streamlit support to enable custom domain

### Heroku
```bash
heroku domains:add dashboard.yourdomain.com
# Follow DNS instructions provided
```

### DigitalOcean
1. Go to App settings → Domains
2. Add custom domain
3. Update DNS records as instructed

---

## Scaling Considerations

### When to scale:
- \>1000 daily users
- Slow page loads
- Database query timeouts
- High API costs

### How to scale:
1. **Database:** Upgrade Supabase plan
2. **Compute:** Increase dyno/instance size
3. **Caching:** Add Redis for session data
4. **CDN:** Use Cloudflare for assets
5. **Load balancing:** Multiple instances

---

## Troubleshooting Deployment

### "Module not found"
→ Check `requirements.txt` is complete

### "Port already in use"
→ Streamlit is trying default port, specify with `--server.port`

### "Database connection failed"
→ Check environment variables are set correctly

### "Page loads slowly"
→ Add `@st.cache_data` to expensive functions

### "AI insights timeout"
→ Increase Claude API timeout or use async calls

---

## Cost Breakdown

### Free Tier (Hobby)
- **Hosting:** Streamlit Cloud (Free)
- **Database:** Supabase Free (500MB)
- **AI:** Claude Free ($5 credit)
- **Total:** $0/month

### Production Tier
- **Hosting:** Heroku Eco ($7/mo)
- **Database:** Supabase Pro ($25/mo)
- **AI:** Claude API (~$10-50/mo depending on usage)
- **Domain:** $12/year
- **Total:** ~$42-82/month

### Enterprise Tier
- **Hosting:** DigitalOcean App Platform ($50/mo)
- **Database:** Supabase Team ($599/mo)
- **AI:** Claude API (~$100-500/mo)
- **CDN:** Cloudflare Pro ($20/mo)
- **Monitoring:** DataDog ($15/mo)
- **Total:** ~$784-1184/month

---

## Support Resources

- [Streamlit Deployment Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Supabase Production Checklist](https://supabase.com/docs/guides/platform/going-into-prod)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)

---

**Ready to deploy! 🚀**

Start with Streamlit Cloud (free), then upgrade as you grow.
