# Render Python 3.13 / psycopg2 Fix

## The Problem

Render is using Python 3.13 by default, but `psycopg2-binary` has compatibility issues with Python 3.13, causing this error:

```
ImportError: undefined symbol: _PyInterpreterState_Get
```

## Solution: Manual Configuration (Required)

Since `runtime.txt` and `.python-version` may not work with Blueprint deployments, you need to **manually configure Python version in Render dashboard**.

### Step-by-Step Fix:

#### 1. Go to Your Render Dashboard
- Visit https://dashboard.render.com
- Find your `stock-market-app` web service
- Click on it

#### 2. Change Python Version
- Click on "Settings" (left sidebar)
- Scroll down to "Build & Deploy" section
- Find **"Python Version"** dropdown
- Select **"3.11"** or **"3.11.7"**
- Click **"Save Changes"**

#### 3. Trigger Manual Deploy
- Go to "Manual Deploy" button (top right)
- Select "Clear build cache & deploy"
- Click "Deploy"

#### 4. Monitor the Build
- Go to "Logs" tab
- Watch for: `==> Using Python version: 3.11.x`
- Build should now succeed!

---

## Alternative: Delete and Redeploy

If the above doesn't work:

### Option A: Delete Service and Use Blueprint

1. **Delete the existing web service**
   - Dashboard → Your service → Settings → Delete Service

2. **Redeploy using Blueprint**
   - Dashboard → "New +" → "Blueprint"
   - Select `StockMarketApp` repository
   - Click "Apply"
   - Render will read render.yaml with correct settings

3. **Manually add Python version in environment**
   - While deploying, go to Settings
   - Set Python Version to 3.11
   - Save and redeploy

### Option B: Create New Service Manually

1. **Create PostgreSQL Database First**
   - Dashboard → "New +" → "PostgreSQL"
   - Name: `stock-market-db`
   - Click "Create"
   - Copy "Internal Database URL"

2. **Create Web Service**
   - Dashboard → "New +" → "Web Service"
   - Connect GitHub: `StockMarketApp`
   - Configure:
     - **Python Version**: 3.11
     - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && python init_db.py`
     - **Start Command**: `gunicorn wsgi:app`
   - Environment Variables:
     - `PYTHON_VERSION`: `3.11`
     - `DATABASE_URL`: (paste Internal Database URL)
     - `SECRET_KEY`: (auto-generate)
     - `FLASK_ENV`: `production`
     - `OPENAI_API_KEY`: (your key)
   - Click "Create Web Service"

---

## Verify Python Version

After deployment starts, check the logs:

```bash
# Should see:
==> Using Python version: 3.11.x
==> Installing dependencies
...
Successfully installed psycopg2-binary-2.9.10
```

If you still see `3.13`, Python version setting didn't apply.

---

## Nuclear Option: Use Alternative PostgreSQL Driver

If all else fails, switch to `psycopg` (version 3) which supports Python 3.13:

### Update requirements.txt:
```txt
# Remove this line:
# psycopg2-binary>=2.9.10

# Add this instead:
psycopg[binary]>=3.1.0
```

### Update config.py:
```python
# In SQLALCHEMY_DATABASE_URI, change driver:
if database_url:
    # For psycopg3, use postgresql+psycopg://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
```

**Note:** Only use this if Python 3.11 setting doesn't work!

---

## Why This Happens

1. **Render defaults to latest Python** (3.13 as of late 2024)
2. **psycopg2-binary has C extensions** that aren't compiled for Python 3.13 yet
3. **Blueprint deployments** may not respect `runtime.txt` or `.python-version`
4. **Manual configuration** in dashboard is most reliable

---

## Expected Result

✅ Build log shows Python 3.11.x
✅ psycopg2-binary installs successfully
✅ Database connection works
✅ App starts without errors
✅ Can create users, stocks, trades
✅ Chat messages persist in PostgreSQL

---

## Still Having Issues?

### Check These:

1. **Python Version Actually Changed?**
   - Look at build logs for "Using Python version"
   - If still 3.13, setting didn't apply

2. **Database Connection String Correct?**
   - Should start with `postgresql://` or `postgres://`
   - Should be "Internal Database URL" not "External"

3. **All Environment Variables Set?**
   - `DATABASE_URL` - from PostgreSQL database
   - `SECRET_KEY` - auto-generated
   - `OPENAI_API_KEY` - your OpenAI key

4. **Database and Service in Same Region?**
   - Both should be in same region (Oregon recommended)

---

## Quick Test After Deploy

```bash
# SSH into Render service (if available) or use Dashboard shell
python --version
# Should show: Python 3.11.x

python -c "import psycopg2; print('psycopg2 working!')"
# Should print: psycopg2 working!

psql $DATABASE_URL -c "SELECT version();"
# Should show PostgreSQL version
```

---

## Summary

**The fix requires manual intervention in Render Dashboard because:**
- Blueprint deployments may override `runtime.txt`
- Dashboard settings take precedence
- Python version must be explicitly set to 3.11

**Manual steps are necessary** - this is a known Render quirk with Blueprint deployments.

Good luck! 🚀
