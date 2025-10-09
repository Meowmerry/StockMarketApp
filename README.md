# Stock Market Web Application

A full-stack stock market web application built with **Python only** - no JavaScript frameworks required. This application allows users to manage their stock portfolio, execute trades, and track their investments with real-time P&L calculations.

## 🚀 Features

### Core Functionality
- **User Authentication**: Register, login, logout with secure password hashing
- **Stock Management**: CRUD operations for stock records (ticker, name, sector, price, shares outstanding)
- **Trade Execution**: Buy/sell trades with quantity, price, and timestamp tracking
- **Portfolio View**: Real-time portfolio aggregation with unrealized P&L calculations
- **Price Simulation**: Simulate market conditions (random changes, crashes, rallies)
- **REST API**: Complete JSON API for all operations
- **Responsive UI**: Modern Bootstrap-based interface with Jinja2 templates

### Technical Features
- **Backend**: Flask + SQLAlchemy
- **Frontend**: Server-rendered HTML templates (Jinja2)
- **Database**: SQLite (easily configurable for PostgreSQL)
- **Authentication**: Flask-Login with secure password hashing
- **API**: RESTful endpoints with JSON responses
- **Testing**: Comprehensive unit and integration tests

## 📋 Requirements

- Python 3.8+
- pip (Python package installer)

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python run.py
   ```
   This will create the database and start the development server.

4. **Populate with sample data (optional)**
   ```bash
   python sample_data.py
   ```

## 🚀 Running the Application

### Development Mode
```bash
python run.py
```

The application will be available at `http://localhost:5001`

### Production Mode
```bash
export FLASK_ENV=production
python run.py
```

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

## 🔧 Configuration

The application uses environment variables for configuration:

```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///stock_market.db"
export FLASK_ENV="development"
```

For PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:password@localhost/stock_market"
```

## 🏗️ Project Structure

```
stock_market_app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── utils.py             # Utility functions
│   ├── auth/                # Authentication blueprint
│   ├── main/                # Main routes blueprint
│   ├── stocks/              # Stocks blueprint
│   ├── trades/              # Trades blueprint
│   ├── portfolio/           # Portfolio blueprint
│   ├── api/                 # API blueprint
│   ├── admin/               # Admin/simulation blueprint
│   └── templates/           # Jinja2 templates
├── tests/                   # Test files
├── run.py                   # Application entry point
├── sample_data.py           # Sample data script
├── requirements.txt         # Python dependencies
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

## 🎯 Future Enhancements

Potential improvements for the application:

- Real-time stock price feeds
- Advanced charting and analytics
- Email notifications for price alerts
- Multi-currency support
- Advanced portfolio analytics
- Social features (following other traders)
- Mobile app integration
- Real-time WebSocket updates

---

**Built with ❤️ using Python, Flask, and modern web technologies.**
