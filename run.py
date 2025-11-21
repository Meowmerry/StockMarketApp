from app import create_app, db
from flask_migrate import upgrade

app = create_app()

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized.")

@app.cli.command()
def populate_sample_data():
    """Populate database with sample data."""
    from app.models import User, Stock, Trade
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    import random
    
    # Create sample users
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'password': 'password123'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'password123'},
        {'username': 'bob_trader', 'email': 'bob@example.com', 'password': 'password123'}
    ]
    
    for user_data in users_data:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password'])
            )
            db.session.add(user)
    
    # Create sample stocks
    stocks_data = [
        {'ticker': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology', 'price': 175.50, 'shares_outstanding': 15500000000},
        {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology', 'price': 142.30, 'shares_outstanding': 12600000000},
        {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology', 'price': 378.85, 'shares_outstanding': 7420000000},
        {'ticker': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Automotive', 'price': 248.50, 'shares_outstanding': 3170000000},
        {'ticker': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary', 'price': 155.20, 'shares_outstanding': 10400000000}
    ]
    
    for stock_data in stocks_data:
        if not Stock.query.filter_by(ticker=stock_data['ticker']).first():
            stock = Stock(**stock_data)
            db.session.add(stock)
    
    db.session.commit()
    
    # Create sample trades
    users = User.query.all()
    stocks = Stock.query.all()
    
    for user in users:
        for _ in range(5):  # 5 trades per user
            stock = random.choice(stocks)
            side = random.choice(['buy', 'sell'])
            quantity = random.randint(1, 100)
            price = stock.price + random.uniform(-10, 10)  # Price variation
            timestamp = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            trade = Trade(
                user_id=user.id,
                stock_id=stock.id,
                side=side,
                quantity=quantity,
                price=price,
                timestamp=timestamp
            )
            db.session.add(trade)
    
    db.session.commit()
    print("Sample data populated successfully.")

if __name__ == '__main__':
    app.secret_key = "super secret key" # Needed for session management # https://stackoverflow.com/questions/26080872/secret-key-not-set-in-flask-session-using-the-flask-session-extension/26080974#26080974
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)



