from flask import render_template, jsonify
from flask_login import login_required, current_user
from app.models import Trade
from app.portfolio import bp

@bp.route('/')
@login_required
def index():
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
    
    return render_template('portfolio/index.html', 
                         portfolio=portfolio,
                         total_value=total_value,
                         total_cost=total_cost,
                         total_unrealized_pnl=total_unrealized_pnl,
                         total_unrealized_pnl_percent=total_unrealized_pnl_percent)

@bp.route('/api')
@login_required
def api():
    # Get user's portfolio summary for API
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    
    portfolio = {}
    total_value = 0
    total_cost = 0
    
    for trade in trades:
        ticker = trade.stock.ticker
        if ticker not in portfolio:
            portfolio[ticker] = {
                'ticker': ticker,
                'name': trade.stock.name,
                'shares': 0,
                'total_cost': 0,
                'avg_price': 0,
                'current_price': float(trade.stock.price)
            }
        
        if trade.side == 'buy':
            portfolio[ticker]['shares'] += trade.quantity
            portfolio[ticker]['total_cost'] += trade.quantity * trade.price
        else:  # sell
            portfolio[ticker]['shares'] -= trade.quantity
            portfolio[ticker]['total_cost'] -= trade.quantity * trade.price
        
        if portfolio[ticker]['shares'] > 0:
            portfolio[ticker]['avg_price'] = float(portfolio[ticker]['total_cost'] / portfolio[ticker]['shares'])
    
    # Remove positions with 0 shares
    portfolio = {k: v for k, v in portfolio.items() if v['shares'] > 0}
    
    # Calculate current value and P&L
    for ticker, position in portfolio.items():
        current_price = position['current_price']
        position['current_value'] = position['shares'] * current_price
        position['unrealized_pnl'] = position['current_value'] - position['total_cost']
        position['unrealized_pnl_percent'] = (position['unrealized_pnl'] / position['total_cost']) * 100 if position['total_cost'] > 0 else 0
        
        total_value += position['current_value']
        total_cost += position['total_cost']
    
    total_unrealized_pnl = total_value - total_cost
    total_unrealized_pnl_percent = (total_unrealized_pnl / total_cost) * 100 if total_cost > 0 else 0
    
    return jsonify({
        'portfolio': list(portfolio.values()),
        'summary': {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_unrealized_pnl_percent': total_unrealized_pnl_percent
        }
    })
