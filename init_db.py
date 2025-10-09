#!/usr/bin/env python3
"""
Database initialization script for Render.com deployment
"""

from app import create_app, db
from app.models import User, Stock, Trade
import os

def init_database():
    """Initialize database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if we already have data
        if User.query.first() is not None:
            print("✅ Database already has data")
            return
        
        # Create sample data
        print("📊 Creating sample data...")
        
        # Create sample users
        user1 = User(
            username='demo_user',
            email='demo@example.com'
        )
        user1.set_password('demo123')
        
        user2 = User(
            username='trader_john',
            email='john@example.com'
        )
        user2.set_password('password123')
        
        db.session.add(user1)
        db.session.add(user2)
        
        # Create sample stocks
        stocks_data = [
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50, 'sector': 'Technology'},
            {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 142.30, 'sector': 'Technology'},
            {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'price': 378.85, 'sector': 'Technology'},
            {'ticker': 'TSLA', 'name': 'Tesla Inc.', 'price': 248.50, 'sector': 'Automotive'},
            {'ticker': 'AMZN', 'name': 'Amazon.com Inc.', 'price': 145.86, 'sector': 'E-commerce'},
        ]
        
        for stock_data in stocks_data:
            stock = Stock(**stock_data)
            db.session.add(stock)
        
        # Create sample trades
        trades_data = [
            {'user_id': 1, 'stock_id': 1, 'quantity': 10, 'price': 175.00, 'trade_type': 'buy'},
            {'user_id': 1, 'stock_id': 2, 'quantity': 5, 'price': 142.00, 'trade_type': 'buy'},
            {'user_id': 2, 'stock_id': 3, 'quantity': 8, 'price': 378.50, 'trade_type': 'buy'},
            {'user_id': 2, 'stock_id': 4, 'quantity': 3, 'price': 248.00, 'trade_type': 'buy'},
        ]
        
        for trade_data in trades_data:
            trade = Trade(**trade_data)
            db.session.add(trade)
        
        # Commit all changes
        db.session.commit()
        print("✅ Sample data created successfully!")
        print(f"   - Users: {User.query.count()}")
        print(f"   - Stocks: {Stock.query.count()}")
        print(f"   - Trades: {Trade.query.count()}")

if __name__ == '__main__':
    init_database()
