# 🚀 Deployment Checklist for Render.com

Follow this checklist to successfully deploy your Stock Market App with PostgreSQL backend.

## ✅ Pre-Deployment Checklist

### 1. Code is Ready
- [x] All changes committed to Git
- [x] Code pushed to GitHub
- [x] `render.yaml` is configured
- [x] `requirements.txt` includes all dependencies
- [x] `.gitignore` excludes sensitive files

### 2. Configuration Files
- [x] `config.py` handles PostgreSQL URLs
- [x] `render.yaml` defines database and web service
- [x] Environment variables documented in `.env.example`

### 3. Dependencies
- [x] Flask and extensions installed
- [x] PostgreSQL driver (psycopg2-binary) included
- [x] OpenAI library included
- [x] Gunicorn for production server

## 🎯 Deployment Steps on Render.com

### Option A: Using Blueprint (Recommended - Automated)

1. **Navigate to Render Dashboard**
   - Go to https://dashboard.render.com
   - Click "New +" in top right

2. **Select Blueprint**
   - Choose "Blueprint"
   - Connect your GitHub account if not already connected

3. **Select Repository**
   - Find and select: `StockMarketApp`
   - Branch: `main`
   - Click "Connect"

4. **Review Blueprint**
   Render will detect `render.yaml` and show:
   - ✅ PostgreSQL Database: `stock-market-db`
   - ✅ Web Service: `stock-market-app`
   - ✅ Automatic connection between them

5. **Customize Service Names (Optional)**
   - Database name: `stock-market-db` (or customize)
   - Web service: `stock-market-app` (or customize)

6. **Click "Apply"**
   - Render will start provisioning:
     - Creating PostgreSQL database (~2-3 minutes)
     - Building web service (~5-10 minutes)
     - Running build command
     - Starting application

7. **Add OpenAI API Key**
   - While deploying, go to web service
   - Click "Environment" tab
   - Add environment variable:
     - **Key**: `OPENAI_API_KEY`
     - **Value**: `sk-your-actual-key`
   - Click "Save Changes"

8. **Wait for Deployment**
   - Watch logs in real-time
   - Look for: "Application startup complete"
   - Status should turn to "Live"

9. **Get Your URL**
   - Your app URL: `https://stock-market-app-XXXX.onrender.com`
   - Copy and visit in browser

### Option B: Manual Setup

If you prefer manual control:

#### Step 1: Create PostgreSQL Database

1. Dashboard → "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `stock-market-db`
   - **Database**: `stock_market_db`
   - **User**: `stock_market_user`
   - **Region**: Oregon (or closest to you)
   - **PostgreSQL Version**: 15
   - **Plan**: Free
3. Click "Create Database"
4. Wait 2-3 minutes for provisioning
5. Copy "Internal Database URL"

#### Step 2: Create Web Service

1. Dashboard → "New +" → "Web Service"
2. Connect GitHub repository: `StockMarketApp`
3. Configure:
   - **Name**: `stock-market-app`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python init_db.py
     ```
   - **Start Command**:
     ```bash
     gunicorn wsgi:app
     ```
   - **Plan**: Free

4. **Add Environment Variables:**
   - `SECRET_KEY`: (auto-generate or use custom)
   - `DATABASE_URL`: (paste Internal Database URL)
   - `FLASK_ENV`: `production`
   - `OPENAI_API_KEY`: `sk-your-openai-key`

5. Click "Create Web Service"

## 🔍 Verification Steps

After deployment completes:

### 1. Check Service Status
- [ ] Web service shows "Live" status
- [ ] Database shows "Available" status
- [ ] No errors in logs

### 2. Test Basic Functionality
- [ ] Homepage loads: `https://your-app.onrender.com`
- [ ] User registration works: `/auth/register`
- [ ] Login works: `/auth/login`
- [ ] Can view stocks: `/stocks`

### 3. Test Database Persistence
- [ ] Create a test user account
- [ ] Add a stock
- [ ] Create a trade
- [ ] Check if data persists after service restart

### 4. Test AI Chatbot
- [ ] Navigate to `/chat`
- [ ] Send a test message
- [ ] Verify response from OpenAI
- [ ] Test floating widget

### 5. Test Data Persistence
```bash
# In Render web service shell:
psql $DATABASE_URL

# Check tables exist
\dt

# Count records
SELECT COUNT(*) FROM "user";
SELECT COUNT(*) FROM stock;
SELECT COUNT(*) FROM trade;
SELECT COUNT(*) FROM chat_message;

# Exit
\q
```

## 🐛 Troubleshooting

### Deployment Failed

**Check Logs:**
- Go to web service → Logs tab
- Look for error messages

**Common Issues:**

1. **Build Failed - Missing Dependencies**
   ```
   Error: ModuleNotFoundError: No module named 'X'
   ```
   **Fix:** Add missing package to `requirements.txt`

2. **Database Connection Error**
   ```
   Error: could not connect to database
   ```
   **Fix:**
   - Verify DATABASE_URL is set correctly
   - Use "Internal Database URL" not external
   - Check database is in same region

3. **Init Script Failed**
   ```
   Error: relation "user" already exists
   ```
   **Fix:** This is normal if tables already exist

4. **OpenAI API Error**
   ```
   Error: Invalid API key
   ```
   **Fix:**
   - Check OPENAI_API_KEY is set correctly
   - Verify key is active in OpenAI dashboard

### Application Not Loading

1. **Check Service Status**
   - Should show "Live" not "Deploy failed"

2. **Check Health Check**
   - Render pings `/` every 30 seconds
   - Must return 200 OK

3. **Check Logs**
   ```
   # Look for:
   Application startup complete
   Listening at: http://0.0.0.0:10000
   ```

### Database Issues

1. **Connection Refused**
   - Use Internal URL, not External
   - Verify service and DB in same region

2. **Too Many Connections**
   - Free tier has connection limits
   - Check for connection leaks in code

3. **Data Not Persisting**
   - Verify using PostgreSQL not SQLite
   - Check DATABASE_URL environment variable

## 🔄 Redeployment

### Automatic Redeployment
Render auto-deploys when you push to GitHub:
```bash
git add .
git commit -m "Update feature X"
git push origin main
# Render automatically redeploys
```

### Manual Redeployment
1. Go to web service dashboard
2. Click "Manual Deploy" → "Deploy latest commit"
3. Or "Clear build cache & deploy" if dependencies changed

## 📊 Monitoring

### Check Application Health
- **Render Dashboard**: Shows uptime, response times
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory usage (paid plans)

### Database Monitoring
- **Render Dashboard**: Database metrics
- **Usage**: Storage, connections
- **Free Tier Limits**:
  - Storage: 1 GB
  - Connections: Limited
  - Retention: 90 days inactive

### Set Up Alerts
- Email notifications for service down
- Slack/Discord webhooks
- Custom monitoring tools

## 💰 Cost Management

### Free Tier Includes:
- ✅ Web service (750 hrs/month)
- ✅ PostgreSQL database (1 GB)
- ✅ Auto-deploys from GitHub
- ✅ Free SSL certificate
- ⚠️ Service spins down after 15 min inactivity
- ⚠️ Cold start ~30 seconds

### Keep Service Active:
```bash
# Use a uptime monitor (every 10 minutes)
# Services: UptimeRobot, Pingdom, StatusCake
URL to ping: https://your-app.onrender.com
```

### When to Upgrade:
- Need 24/7 availability (no spin down)
- More than 1 GB database
- Automated backups
- Custom domain without Render branding

## 🔒 Security Checklist

### Before Going Live:
- [ ] SECRET_KEY is randomly generated
- [ ] OPENAI_API_KEY is kept secret
- [ ] Database credentials not exposed
- [ ] HTTPS enabled (automatic on Render)
- [ ] CSRF protection enabled (WTF_CSRF_ENABLED=True)
- [ ] Strong password hashing (already configured)

### Regular Maintenance:
- [ ] Rotate SECRET_KEY periodically
- [ ] Monitor OpenAI usage and costs
- [ ] Review database size and clean old data
- [ ] Update dependencies for security patches

## 📝 Post-Deployment Tasks

### 1. Test Thoroughly
- Create test accounts
- Execute sample trades
- Test all features

### 2. Populate Data
```bash
# If init_db.py didn't run automatically:
# SSH into Render service or use shell
python init_db.py
```

### 3. Share Your App
Your app is live at:
```
https://stock-market-app-XXXX.onrender.com
```

### 4. Document
- Note your app URL
- Save database credentials (in secure location)
- Document any custom configurations

## 🎉 Success!

Your Stock Market App is now live with:
- ✅ PostgreSQL database (persistent storage)
- ✅ AI chatbot powered by OpenAI
- ✅ Auto-deploy from GitHub
- ✅ Free hosting on Render
- ✅ HTTPS enabled
- ✅ Production-ready configuration

---

## 📚 Resources

- [Render Documentation](https://render.com/docs)
- [PostgreSQL on Render](https://render.com/docs/databases)
- [Troubleshooting Guide](https://render.com/docs/troubleshooting)
- [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)
- [CHATBOT_SETUP.md](CHATBOT_SETUP.md)

---

**Need Help?**
- Check Render logs for error messages
- Review documentation files
- Test locally first with same configuration
- Reach out to Render support for platform issues

Good luck with your deployment! 🚀
