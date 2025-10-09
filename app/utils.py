import random
from decimal import Decimal
from app import db
from app.models import Stock

def simulate_price_changes(volatility=0.02, max_stocks=None):
    """
    Simulate price changes for stocks with random fluctuations.
    
    Args:
        volatility (float): Maximum percentage change per simulation (default 2%)
        max_stocks (int): Maximum number of stocks to update (None for all)
    
    Returns:
        dict: Summary of price changes
    """
    stocks = Stock.query.limit(max_stocks).all() if max_stocks else Stock.query.all()
    changes = []
    
    for stock in stocks:
        # Generate random price change between -volatility and +volatility
        change_percent = random.uniform(-volatility, volatility)
        old_price = float(stock.price)
        new_price = old_price * (1 + change_percent)
        
        # Update stock price
        stock.price = Decimal(str(round(new_price, 2)))
        
        changes.append({
            'ticker': stock.ticker,
            'old_price': old_price,
            'new_price': new_price,
            'change': new_price - old_price,
            'change_percent': change_percent * 100
        })
    
    db.session.commit()
    
    return {
        'updated_count': len(stocks),
        'changes': changes
    }

def simulate_market_crash(crash_percent=0.15):
    """
    Simulate a market crash by reducing all stock prices.
    
    Args:
        crash_percent (float): Percentage to reduce all prices (default 15%)
    
    Returns:
        dict: Summary of the crash
    """
    stocks = Stock.query.all()
    changes = []
    
    for stock in stocks:
        old_price = float(stock.price)
        new_price = old_price * (1 - crash_percent)
        stock.price = Decimal(str(round(new_price, 2)))
        
        changes.append({
            'ticker': stock.ticker,
            'old_price': old_price,
            'new_price': new_price,
            'change': new_price - old_price,
            'change_percent': -crash_percent * 100
        })
    
    db.session.commit()
    
    return {
        'updated_count': len(stocks),
        'crash_percent': crash_percent,
        'changes': changes
    }

def simulate_market_rally(rally_percent=0.10):
    """
    Simulate a market rally by increasing all stock prices.
    
    Args:
        rally_percent (float): Percentage to increase all prices (default 10%)
    
    Returns:
        dict: Summary of the rally
    """
    stocks = Stock.query.all()
    changes = []
    
    for stock in stocks:
        old_price = float(stock.price)
        new_price = old_price * (1 + rally_percent)
        stock.price = Decimal(str(round(new_price, 2)))
        
        changes.append({
            'ticker': stock.ticker,
            'old_price': old_price,
            'new_price': new_price,
            'change': new_price - old_price,
            'change_percent': rally_percent * 100
        })
    
    db.session.commit()
    
    return {
        'updated_count': len(stocks),
        'rally_percent': rally_percent,
        'changes': changes
    }
