#!/usr/bin/env python3
"""
Sample data script for Stock Market App.
This script populates the database with sample users, stocks, and trades.
"""

from app import create_app, db
from app.models import User, Stock, Trade
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_sample_users():
    """Create sample users."""
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'password': 'password123'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'password123'},
        {'username': 'bob_trader', 'email': 'bob@example.com', 'password': 'password123'},
        {'username': 'alice_investor', 'email': 'alice@example.com', 'password': 'password123'},
        {'username': 'demo_user', 'email': 'demo@example.com', 'password': 'demo123'}
    ]
    
    created_users = []
    for user_data in users_data:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password'])
            )
            db.session.add(user)
            created_users.append(user)
            print(f"Created user: {user_data['username']}")
    
    db.session.commit()
    return created_users

def create_sample_stocks():
    """Create sample stocks."""
    stocks_data = [
        {
            'ticker': 'AAPL', 
            'name': 'Apple Inc.', 
            'sector': 'Technology', 
            'price': 175.50, 
            'shares_outstanding': 15500000000
        },
        {
            'ticker': 'GOOGL', 
            'name': 'Alphabet Inc.', 
            'sector': 'Technology', 
            'price': 142.30, 
            'shares_outstanding': 12600000000
        },
        {
            'ticker': 'MSFT', 
            'name': 'Microsoft Corporation', 
            'sector': 'Technology', 
            'price': 378.85, 
            'shares_outstanding': 7420000000
        },
        {
            'ticker': 'TSLA', 
            'name': 'Tesla Inc.', 
            'sector': 'Automotive', 
            'price': 248.50, 
            'shares_outstanding': 3170000000
        },
        {
            'ticker': 'AMZN', 
            'name': 'Amazon.com Inc.', 
            'sector': 'Consumer Discretionary', 
            'price': 155.20, 
            'shares_outstanding': 10400000000
        },
        {
            'ticker': 'META', 
            'name': 'Meta Platforms Inc.', 
            'sector': 'Technology', 
            'price': 324.75, 
            'shares_outstanding': 2700000000
        },
        {
            'ticker': 'NVDA', 
            'name': 'NVIDIA Corporation', 
            'sector': 'Technology', 
            'price': 875.25, 
            'shares_outstanding': 2480000000
        },
        {
            'ticker': 'BRK.B', 
            'name': 'Berkshire Hathaway Inc.', 
            'sector': 'Financial Services', 
            'price': 385.40, 
            'shares_outstanding': 1500000000
        },
        {
            'ticker': 'JPM', 
            'name': 'JPMorgan Chase & Co.', 
            'sector': 'Financial Services', 
            'price': 175.80, 
            'shares_outstanding': 2900000000
        },
        {
            'ticker': 'JNJ', 
            'name': 'Johnson & Johnson', 
            'sector': 'Healthcare', 
            'price': 158.45, 
            'shares_outstanding': 2600000000
        }
    ]
    
    created_stocks = []
    for stock_data in stocks_data:
        if not Stock.query.filter_by(ticker=stock_data['ticker']).first():
            stock = Stock(**stock_data)
            db.session.add(stock)
            created_stocks.append(stock)
            print(f"Created stock: {stock_data['ticker']} - {stock_data['name']}")
    
    db.session.commit()
    return created_stocks

def create_sample_trades(users, stocks):
    """Create sample trades."""
    created_trades = []
    
    for user in users:
        # Each user gets 8-15 trades
        num_trades = random.randint(8, 15)
        
        for _ in range(num_trades):
            stock = random.choice(stocks)
            side = random.choice(['buy', 'sell'])
            
            # For sell trades, make sure user has some shares first
            if side == 'sell':
                # Check if user has any shares of this stock
                user_shares = 0
                user_trades = Trade.query.filter_by(user_id=user.id, stock_id=stock.id).all()
                for trade in user_trades:
                    if trade.side == 'buy':
                        user_shares += trade.quantity
                    else:
                        user_shares -= trade.quantity
                
                if user_shares <= 0:
                    side = 'buy'  # Change to buy if no shares
            
            # Generate realistic trade parameters
            if side == 'buy':
                quantity = random.randint(1, 200)
            else:
                # For sell trades, don't sell more than user owns
                user_shares = 0
                user_trades = Trade.query.filter_by(user_id=user.id, stock_id=stock.id).all()
                for trade in user_trades:
                    if trade.side == 'buy':
                        user_shares += trade.quantity
                    else:
                        user_shares -= trade.quantity
                quantity = random.randint(1, min(user_shares, 200))
            
            # Price variation: current price ± 5%
            price_variation = random.uniform(-0.05, 0.05)
            price = float(stock.price) * (1 + price_variation)
            
            # Random timestamp within the last 90 days
            timestamp = datetime.utcnow() - timedelta(days=random.randint(1, 90))
            
            trade = Trade(
                user_id=user.id,
                stock_id=stock.id,
                side=side,
                quantity=quantity,
                price=price,
                timestamp=timestamp
            )
            db.session.add(trade)
            created_trades.append(trade)
    
    db.session.commit()
    print(f"Created {len(created_trades)} trades")
    return created_trades

def main():
    """Main function to populate sample data."""
    app = create_app()
    
    with app.app_context():
        print("Creating sample data...")
        
        # Create users
        users = create_sample_users()
        print(f"Created {len(users)} users")
        
        # Create stocks
        stocks = create_sample_stocks()
        print(f"Created {len(stocks)} stocks")
        
        # Create trades
        trades = create_sample_trades(users, stocks)
        print(f"Created {len(trades)} trades")
        
        print("\nSample data created successfully!")
        print("\nSample login credentials:")
        print("Username: john_doe, Password: password123")
        print("Username: jane_smith, Password: password123")
        print("Username: demo_user, Password: demo123")
        print("\nYou can now run the application and test with these accounts.")

if __name__ == '__main__':
    main()
