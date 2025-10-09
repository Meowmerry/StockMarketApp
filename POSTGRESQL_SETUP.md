# PostgreSQL Database Setup Guide

This guide explains how to set up PostgreSQL for your Stock Market App, both locally and on Render.com.

## 🎯 Why PostgreSQL?

✅ **Production-ready** - Robust, ACID-compliant relational database
✅ **Persistent data** - Data survives server restarts (unlike SQLite on Render)
✅ **Scalable** - Handles concurrent connections and large datasets
✅ **Free tier** - Render offers free PostgreSQL databases
✅ **Better performance** - Optimized for web applications

---

## 🚀 Quick Start: Render.com (Recommended)

The easiest way to get PostgreSQL is using Render's managed database.

### Automatic Setup (Using render.yaml)

Your `render.yaml` is already configured! Just:

1. **Commit and push your code:**
   ```bash
   git add .
   git commit -m "Migrate to PostgreSQL database"
   git push
   ```

2. **Deploy on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically:
     - Create PostgreSQL database
     - Create web service
     - Connect them together

3. **Done!** Your app will automatically use PostgreSQL.

### Manual Setup on Render

If you prefer manual setup:

1. **Create PostgreSQL Database:**
   - Dashboard → "New +" → "PostgreSQL"
   - Name: `stock-market-db`
   - Database: `stock_market_db`
   - User: `stock_market_user`
   - Region: Same as your web service
   - Plan: Free
   - Click "Create Database"

2. **Connect to Web Service:**
   - Go to your web service settings
   - Environment tab
   - Add environment variable:
     - Key: `DATABASE_URL`
     - Value: Copy "Internal Database URL" from PostgreSQL dashboard
   - Save changes

3. **Redeploy:**
   - Your service will restart with PostgreSQL

---

## 💻 Local Development Setup

### Option 1: Continue Using SQLite (Easiest)

SQLite works fine for local development:

```bash
# In .env file
DATABASE_URL=sqlite:///stock_market.db
```

Your code automatically falls back to SQLite if DATABASE_URL is not set.

### Option 2: Local PostgreSQL (Recommended for Production Parity)

#### Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

#### Create Database and User

```bash
# Access PostgreSQL
psql postgres

# Create user
CREATE USER stock_market_user WITH PASSWORD 'your_password';

# Create database
CREATE DATABASE stock_market_db OWNER stock_market_user;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE stock_market_db TO stock_market_user;

# Exit
\q
```

#### Update .env File

```bash
# Replace with your actual credentials
DATABASE_URL=postgresql://stock_market_user:your_password@localhost:5432/stock_market_db
```

#### Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate

# Install PostgreSQL driver
pip install psycopg2-binary

# Initialize database
python init_db.py
```

---

## 🔄 Database Migration

### From SQLite to PostgreSQL

If you have existing SQLite data you want to migrate:

1. **Export data from SQLite:**
   ```bash
   sqlite3 instance/stock_market.db .dump > data_backup.sql
   ```

2. **Manually import data or recreate:**
   ```bash
   # Option 1: Fresh start (recommended)
   python init_db.py

   # Option 2: Use migration tools
   # Install pgloader or use custom migration script
   ```

### Using Flask-Migrate

For schema changes:

```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

---

## 🧪 Testing Database Connection

Create a test script `test_db.py`:

```python
from app import create_app, db
from app.models import User, Stock, Trade, ChatMessage

app = create_app()

with app.app_context():
    try:
        # Test connection
        db.create_all()
        print("✅ Database connection successful!")

        # Test query
        user_count = User.query.count()
        stock_count = Stock.query.count()
        trade_count = Trade.query.count()
        chat_count = ChatMessage.query.count()

        print(f"📊 Database Statistics:")
        print(f"   Users: {user_count}")
        print(f"   Stocks: {stock_count}")
        print(f"   Trades: {trade_count}")
        print(f"   Chat Messages: {chat_count}")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
```

Run it:
```bash
python test_db.py
```

---

## 🛠️ Common PostgreSQL Commands

### psql Commands

```bash
# Connect to database
psql -U stock_market_user -d stock_market_db

# List databases
\l

# List tables
\dt

# Describe table
\d table_name

# View table data
SELECT * FROM user LIMIT 5;

# Exit
\q
```

### Useful Queries

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Count records in all tables
SELECT 'user' as table_name, COUNT(*) FROM "user"
UNION ALL
SELECT 'stock', COUNT(*) FROM stock
UNION ALL
SELECT 'trade', COUNT(*) FROM trade
UNION ALL
SELECT 'chat_message', COUNT(*) FROM chat_message;
```

---

## 🔒 Security Best Practices

1. **Never commit database credentials:**
   - Use environment variables
   - Keep `.env` in `.gitignore`

2. **Use strong passwords:**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

3. **Limit database access:**
   - Use specific user (not postgres superuser)
   - Grant only necessary privileges

4. **Regular backups:**
   ```bash
   # Backup database
   pg_dump -U stock_market_user stock_market_db > backup.sql

   # Restore database
   psql -U stock_market_user stock_market_db < backup.sql
   ```

5. **Monitor usage:**
   - Check Render dashboard for database metrics
   - Set up alerts for storage limits

---

## 🐛 Troubleshooting

### "could not connect to server"

**Solution:**
- Check if PostgreSQL is running: `brew services list` (macOS)
- Check credentials in DATABASE_URL
- Verify database and user exist

### "relation does not exist"

**Solution:**
```bash
# Create tables
python init_db.py

# Or use migrations
flask db upgrade
```

### "password authentication failed"

**Solution:**
- Check username/password in DATABASE_URL
- Reset password if needed:
  ```sql
  ALTER USER stock_market_user WITH PASSWORD 'new_password';
  ```

### Render Database Connection Issues

**Solution:**
1. Use "Internal Database URL" (not external)
2. Check if database and web service are in same region
3. Verify environment variable is set correctly
4. Check Render logs for detailed error messages

### "too many connections"

**Solution:**
- Free tier has connection limits
- Add connection pooling:
  ```python
  # In config.py
  SQLALCHEMY_ENGINE_OPTIONS = {
      'pool_size': 5,
      'pool_recycle': 300,
      'pool_pre_ping': True
  }
  ```

---

## 📊 Render Free Tier Limits

- **Storage:** 1 GB
- **Connections:** Limited concurrent connections
- **Retention:** Database kept for 90 days of inactivity
- **Backups:** Not included in free tier

**Upgrade if you need:**
- More storage
- More concurrent connections
- Automated backups
- Better performance

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Database created successfully
- [ ] `DATABASE_URL` environment variable set
- [ ] App starts without errors
- [ ] Can create user accounts
- [ ] Can add stocks
- [ ] Can create trades
- [ ] Portfolio calculations work
- [ ] Chat messages are stored
- [ ] Data persists after server restart

---

## 🚀 Next Steps

1. **Deploy to Render:** Push code and let render.yaml handle setup
2. **Add data:** Run `python init_db.py` to populate database
3. **Test thoroughly:** Create accounts, trades, use chatbot
4. **Monitor:** Check Render dashboard for database metrics
5. **Backup:** Set up regular backups if using paid tier

---

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Render PostgreSQL Guide](https://render.com/docs/databases)
- [SQLAlchemy PostgreSQL Docs](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)

---

**Your app is now ready for production with PostgreSQL! 🎉**
