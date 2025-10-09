from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Stock, Trade
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    # Get recent stocks and trades for homepage
    recent_stocks = Stock.query.order_by(Stock.created_at.desc()).limit(5).all()
    
    if current_user.is_authenticated:
        recent_trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.timestamp.desc()).limit(5).all()
    else:
        recent_trades = []
    
    return render_template('main/index.html', 
                         recent_stocks=recent_stocks, 
                         recent_trades=recent_trades)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's portfolio summary
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    
    portfolio = {}
    total_value = 0
    total_cost = 0
    
    for trade in trades:
        ticker = trade.stock.ticker
        if ticker not in portfolio:
            portfolio[ticker] = {
                'stock': trade.stock,
                'shares': 0,
                'total_cost': 0,
                'avg_price': 0
            }
        
        if trade.side == 'buy':
            portfolio[ticker]['shares'] += trade.quantity
            portfolio[ticker]['total_cost'] += trade.quantity * trade.price
        else:  # sell
            portfolio[ticker]['shares'] -= trade.quantity
            portfolio[ticker]['total_cost'] -= trade.quantity * trade.price
        
        if portfolio[ticker]['shares'] > 0:
            portfolio[ticker]['avg_price'] = portfolio[ticker]['total_cost'] / portfolio[ticker]['shares']
    
    # Remove positions with 0 shares
    portfolio = {k: v for k, v in portfolio.items() if v['shares'] > 0}
    
    # Calculate current value and P&L
    for ticker, position in portfolio.items():
        current_price = position['stock'].price
        position['current_value'] = position['shares'] * current_price
        position['unrealized_pnl'] = position['current_value'] - position['total_cost']
        position['unrealized_pnl_percent'] = (position['unrealized_pnl'] / position['total_cost']) * 100 if position['total_cost'] > 0 else 0
        
        total_value += position['current_value']
        total_cost += position['total_cost']
    
    total_unrealized_pnl = total_value - total_cost
    total_unrealized_pnl_percent = (total_unrealized_pnl / total_cost) * 100 if total_cost > 0 else 0
    
    return render_template('main/dashboard.html', 
                         portfolio=portfolio,
                         total_value=total_value,
                         total_cost=total_cost,
                         total_unrealized_pnl=total_unrealized_pnl,
                         total_unrealized_pnl_percent=total_unrealized_pnl_percent)
