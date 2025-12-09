# Stock Market Web Application

A full-stack stock market web application built with **Python only** - no JavaScript frameworks required. This application allows users to manage their stock portfolio, execute trades, and track their investments with real-time P&L calculations.

## 🚀 Features

### Core Functionality
- **User Authentication**: Register, login, logout with secure password hashing
- **Stock Management**: CRUD operations for stock records (ticker, name, sector, price, shares outstanding)
- **Trade Execution**: Buy/sell trades with quantity, price, and timestamp tracking
- **Portfolio View**: Real-time portfolio aggregation with unrealized P&L calculations
- **Price Simulation**: Simulate market conditions (random changes, crashes, rallies)
- **AI Chatbot**: Educational AI assistant powered by free local models (no API costs)
- **REST API**: Complete JSON API for all operations
- **Responsive UI**: Modern Bootstrap-based interface with Jinja2 templates

### Technical Features
- **Backend**: Flask + SQLAlchemy
- **Frontend**: Server-rendered HTML templates (Jinja2)
- **Database**: PostgreSQL (with SQLite fallback for local dev)
- **Authentication**: Flask-Login with secure password hashing
- **API**: RESTful endpoints with JSON responses
- **AI Integration**: Ollama with Llama 3.2 (free, local, no API key required)
- **Testing**: Comprehensive unit and integration tests

## 📋 Requirements

- Python 3.8+
- pip (Python package installer)
- Ollama (for AI chatbot) - installation instructions below

## 🛠️ Installation

### Quick Start (Recommended)
```bash
cd stock_market_app
./start.sh
```
This will automatically set up the virtual environment, install dependencies, and start the server.

### Manual Installation

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\ activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and configure:
   # - DATABASE_URL (optional - defaults to SQLite)
   # Note: AI chatbot uses free local models, no API key required!
   ```

   See [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) for database configuration.

4. **Set up AI Chatbot (Ollama)**
   ```bash
   # Install Ollama
   brew install ollama  # Mac/Linux

   # Start Ollama server (in a separate terminal or background)
   ollama serve

   # Download Llama 3.2 model (in another terminal)
   ollama pull llama3.2
   ```

   See the [AI Chatbot Configuration](#ai-chatbot-configuration) section for detailed setup.

5. **Initialize the database**
   ```bash
   python run.py
   ```
   This will create the database and start the development server.

6. **Populate with sample data (optional)**
   ```bash
   python sample_data.py
   ```

## 🚀 Running the Application

### Development Mode

**Important**: Make sure Ollama is running first!

**If using brew services (recommended)**:
```bash
# Start Ollama once (runs in background)
brew services start ollama

# Start Flask app
python run.py
```

**If running manually**:
```bash
# Terminal 1: Start Ollama (keeps this terminal busy)
ollama serve

# Terminal 2: Start Flask app (in a new terminal)
python run.py
```

The application will be available at `http://localhost:5001`

### Production Mode
```bash
export FLASK_ENV=production
python run.py
```

## 🗄️ Database Migrations

This application uses Flask-Migrate (Alembic) to manage database schema changes.

### Adding New Columns or Tables

When you modify your database models in `app/models.py`, follow these steps:

1. **Make your model changes**
   ```python
   # Example: Adding a new column to the Stock model
   class Stock(db.Model):
       # ... existing columns ...
       market_cap = db.Column(db.BigInteger)  # New column
   ```

2. **Apply any pending migrations first**
   ```bash
   flask db upgrade
   ```

3. **Generate a migration script**
   ```bash
   flask db migrate -m "Add market_cap column to Stock table"
   ```
   This creates a new migration file in `migrations/versions/`

4. **Review the generated migration**
   Check the generated file in `migrations/versions/` to ensure it's correct

5. **Apply the migration**
   ```bash
   flask db upgrade
   ```

### Common Migration Commands

```bash
# Initialize migrations (only needed once per project)
flask db init

# Generate a new migration after model changes
flask db migrate -m "Description of changes"

# Apply all pending migrations
flask db upgrade

# Revert the last migration
flask db downgrade

# Show current migration version
flask db current

# Show migration history
flask db history
```

### Migration Best Practices

- Always review auto-generated migrations before applying
- Write descriptive migration messages
- Test migrations on a development database first
- Backup production data before running migrations
- Never edit migrations that have been applied to production

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_auth.py
pytest tests/test_stocks.py
pytest tests/test_trades.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app
```

## 📊 Sample Data

The application includes a sample data script that creates:
- 5 sample users
- 10 popular stocks (AAPL, GOOGL, MSFT, etc.)
- 50+ realistic trades across different users

### Sample Login Credentials
- **Username**: `john_doe`, **Password**: `password123`
- **Username**: `jane_smith`, **Password**: `password123`
- **Username**: `demo_user`, **Password**: `demo123`

## 🌐 API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user

### Stocks
- `GET /api/stocks` - List all stocks
- `POST /api/stocks` - Create new stock
- `GET /api/stocks/{ticker}` - Get specific stock
- `PUT /api/stocks/{ticker}` - Update stock
- `DELETE /api/stocks/{ticker}` - Delete stock

### Trades
- `GET /api/trades` - List user's trades
- `POST /api/trades` - Create new trade

### Portfolio
- `GET /api/portfolio` - Get user's portfolio with P&L

### Example API Usage

```bash
# Register a user
curl -X POST http://localhost:5001/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass"}'

# Login
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Get stocks
curl http://localhost:5001/api/stocks

# Create a trade (requires login)
curl -X POST http://localhost:5001/api/trades \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "side": "buy", "quantity": 10, "price": 150.00}'
```

## 🗄️ Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Hashed password
- `created_at` - Account creation timestamp

### Stocks Table
- `id` - Primary key
- `ticker` - Stock ticker symbol (unique)
- `name` - Company name
- `sector` - Industry sector
- `price` - Current stock price
- `shares_outstanding` - Total shares outstanding
- `created_at` - Stock creation timestamp

### Trades Table
- `id` - Primary key
- `user_id` - Foreign key to users table
- `stock_id` - Foreign key to stocks table
- `side` - 'buy' or 'sell'
- `quantity` - Number of shares
- `price` - Price per share
- `timestamp` - Trade execution timestamp

## 🎮 Using the Application

### 1. User Registration & Login
- Visit `/auth/register` to create a new account
- Use `/auth/login` to access your account

### 2. Managing Stocks
- View all stocks at `/stocks`
- Add new stocks at `/stocks/create`
- Edit stock information at `/stocks/{ticker}/edit`
- View stock details at `/stocks/{ticker}`

### 3. Executing Trades
- View your trades at `/trades`
- Create new trades at `/trades/create`
- Edit trades at `/trades/{id}/edit`
- View trade details at `/trades/{id}`

### 4. Portfolio Management
- View your portfolio at `/portfolio`
- Dashboard overview at `/dashboard`
- Real-time P&L calculations

### 5. Price Simulation
- Access simulation tools at `/admin/simulate`
- Simulate random price changes
- Test market crash scenarios
- Simulate market rallies

### 6. AI Chatbot Assistant
- Access the chat page at `/chat`
- Use the floating chat widget on any page (bottom-right corner)
- Ask educational questions about stocks and investing
- Get portfolio summaries (when logged in)
- Learn about stock market concepts

## 🔧 Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///stock_market.db
```

For PostgreSQL:
```bash
DATABASE_URL=postgresql://user:password@localhost/stock_market
```

### AI Chatbot Configuration

The application uses **Ollama with Llama 3.2** - a free local AI that provides high-quality educational responses about stocks and investing!

**Current Setup**: Ollama + Llama 3.2 (2GB)
- ✅ Free and open-source
- ✅ Runs locally on your computer
- ✅ Educational, accurate responses
- ✅ No API costs or token limits
- ✅ Privacy-focused (all data stays local)

#### Step-by-Step Setup

**Step 1: Install Ollama**

Mac:
```bash
brew install ollama
```

Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Windows: Download from [ollama.ai](https://ollama.ai)

**Step 2: Start Ollama Server**

You have several options for running the Ollama server:

**Option A: Using brew services (Recommended - runs automatically)**
```bash
brew services start ollama
```
This starts Ollama as a background service that will:
- Run automatically when your computer starts
- Restart automatically if it crashes
- Not block your terminal

To stop it later:
```bash
brew services stop ollama
```

To check if it's running:
```bash
brew services list | grep ollama
```

**Option B: Run in foreground (simple but blocks terminal)**
```bash
ollama serve
```
This starts Ollama on `http://localhost:11434` but keeps the terminal busy. You'll need to open a new terminal for other commands. Press `Ctrl+C` to stop it.

**Option C: Run in background manually**
```bash
ollama serve &
```
Runs Ollama in the background so you can continue using the same terminal. To stop it:
```bash
pkill ollama
```

**Step 3: Download the Llama 3.2 Model**

In a new terminal:
```bash
ollama pull llama3.2
```

This downloads the model (~2GB). It only needs to be done once.

**Step 4: Verify Setup**

Test that Ollama is working:
```bash
curl http://localhost:11434/api/tags
```

You should see output showing `llama3.2` is available.

**Step 5: Run Your Flask App**

```bash
python run.py
```

The chatbot will now use Ollama automatically!

#### Alternative Models

You can switch to different models by editing [chat_service.py:15](app/chat_service.py#L15):

```python
# Current (recommended for finance/education)
MODEL_NAME = "llama3.2"

# For faster responses (smaller model)
MODEL_NAME = "phi"  # Run: ollama pull phi

# For better reasoning (larger model)
MODEL_NAME = "mistral"  # Run: ollama pull mistral

# For coding help
MODEL_NAME = "codellama"  # Run: ollama pull codellama
```

After changing the model, download it:
```bash
ollama pull <model-name>
```

Then restart your Flask app.

#### Troubleshooting

**Ollama not responding?**
```bash
# Check if Ollama is running
lsof -i :11434

# Or check brew services
brew services list | grep ollama

# If not running, start it
brew services start ollama  # Recommended
# OR
ollama serve  # Manual start
```

**How to stop Ollama?**
```bash
# If using brew services
brew services stop ollama

# If running manually in foreground
# Press Ctrl+C in the terminal running ollama serve

# If running in background with &
pkill ollama
```

**Model not found?**
```bash
# List installed models
ollama list

# Download the model
ollama pull llama3.2
```

**Slow responses?**
- Llama 3.2 runs on CPU and may take 3-10 seconds
- Try a smaller model like `phi` for faster responses
- Or upgrade to a Mac with Apple Silicon for GPU acceleration

#### Architecture

```
Flask App (port 5001)
    ↓
chat_service.py
    ↓ HTTP POST request
Ollama Server (port 11434)
    ↓
Llama 3.2 Model
    ↓ Generated response
Back to user
```

## 🏗️ Project Structure

```
stock_market_app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models (User, Stock, Trade, ChatMessage)
│   ├── utils.py             # Utility functions
│   ├── chat_prompts.py      # AI chatbot system prompts and templates
│   ├── chat_service.py      # OpenAI API integration service
│   ├── auth/                # Authentication blueprint
│   ├── main/                # Main routes blueprint
│   ├── stocks/              # Stocks blueprint
│   ├── trades/              # Trades blueprint
│   ├── portfolio/           # Portfolio blueprint
│   ├── api/                 # API blueprint
│   ├── admin/               # Admin/simulation blueprint
│   ├── chat/                # AI chatbot blueprint
│   └── templates/           # Jinja2 templates
│       ├── chat/            # Chat templates (index.html, widget.html)
│       └── ...
├── tests/                   # Test files
├── run.py                   # Application entry point
├── init_db.py              # Database initialization script
├── sample_data.py           # Sample data script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🧪 Testing

The application includes comprehensive tests covering:

- **Authentication**: User registration, login, logout
- **Stock CRUD**: Create, read, update, delete operations
- **Trade CRUD**: Trade creation, validation, portfolio calculations
- **API Endpoints**: All REST API functionality
- **Integration Tests**: End-to-end user workflows

Run tests with:
```bash
pytest tests/ -v
```

## 🚀 Deployment

### Using Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Database not found**
   - Run `python run.py` to initialize the database
   - Check database file permissions

2. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Tests failing**
   - Ensure test database is clean
   - Check for missing dependencies

4. **API authentication issues**
   - Ensure user is logged in
   - Check session cookies

### Getting Help

- Check the test files for usage examples
- Review the API documentation above
- Examine the sample data for realistic test cases

## 🤖 AI Chatbot Features

The application includes an intelligent AI chatbot powered by OpenAI GPT:

### What the Chatbot Can Do:
- ✅ Explain stock market concepts and terminology
- ✅ Provide information about stocks in the database
- ✅ Summarize your portfolio holdings (when logged in)
- ✅ Answer educational questions about investing
- ✅ Help users understand their trades and P&L

### What the Chatbot Won't Do:
- ❌ Give personalized investment advice
- ❌ Recommend specific stocks to buy or sell
- ❌ Predict stock prices or market movements
- ❌ Provide financial planning or tax advice

### Usage:
- **Full Chat Page**: Visit `/chat` for a dedicated chat interface
- **Floating Widget**: Use the chat button (bottom-right) on any page
- **Context-Aware**: Automatically accesses your portfolio data when logged in

### Configuration:
The chatbot uses GPT-3.5-turbo for cost-efficiency and includes:
- Safety filters to prevent inappropriate advice requests
- Graceful fallback when API is unavailable
- Conversation history for context
- Rate limit handling

## 🎯 Future Enhancements

Potential improvements for the application:

- Real-time stock price feeds integration
- Advanced charting and analytics
- Email notifications for price alerts
- Multi-currency support
- Advanced portfolio analytics and insights
- Social features (following other traders)
- Mobile app integration
- Real-time WebSocket updates
- Enhanced AI chatbot with more data sources

---

**Built with ❤️ using Python, Flask, and modern web technologies.**
