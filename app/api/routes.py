from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user,login_required, current_user
from app import db
from app.models import User, Stock, Trade
from app.api import bp
from decimal import Decimal
from datetime import datetime

# @bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         data = request.get_json() if request.is_json else request.form
#         username = data.get('username')
#         email = data.get('email')
#         password = data.get('password')
        
#         if not username or not email or not password:
#             error_msg = 'Username, email, and password are required.'
#             if request.is_json:
#                 return jsonify({'error': error_msg}), 400
#             flash(error_msg, 'error')
#             return render_template('auth/register.html')
        
#         if User.query.filter_by(username=username).first():
#             error_msg = 'Username already exists.'
#             if request.is_json:
#                 return jsonify({'error': error_msg}), 400
#             flash(error_msg, 'error')
#             return render_template('auth/register.html')
        
#         if User.query.filter_by(email=email).first():
#             error_msg = 'Email already registered.'
#             if request.is_json:
#                 return jsonify({'error': error_msg}), 400
#             flash(error_msg, 'error')  # error here - no email validation?
#             return render_template('auth/register.html')
        
#         user = User(username=username, email=email)
#         user.set_password(password)
#         db.session.add(user)
#         db.session.commit()
        
#         login_user(user)
        
#         if request.is_json:
#             return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201
        
#         flash('Registration successful!', 'success')
#         return redirect(url_for('main.index'))
    
#     return render_template('auth/register.html')

# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         data = request.get_json() if request.is_json else request.form
#         username = data.get('username')
#         password = data.get('password')
        
#         if not username or not password:
#             error_msg = 'Username and password are required.'
#             if request.is_json:
#                 return jsonify({'error': error_msg}), 400
#             flash(error_msg, 'error')
#             return render_template('auth/login.html')
        
#         user = User.query.filter_by(username=username).first()
        
#         if user and user.check_password(password):
#             login_user(user)
            
#             if request.is_json:
#                 return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
            
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('main.index'))
        
#         error_msg = 'Invalid username or password.'
#         if request.is_json:
#             return jsonify({'error': error_msg}), 401
#         flash(error_msg, 'error')
#         return render_template('auth/login.html')
    
#     return render_template('auth/login.html')


@bp.route('/stocks', methods=['GET'])
def get_stocks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    stocks = Stock.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'stocks': [stock.to_dict() for stock in stocks.items],
        'total': stocks.total,
        'pages': stocks.pages,
        'current_page': stocks.page,
        'per_page': stocks.per_page
    })

@bp.route('/stocks', methods=['POST'])
@login_required
def create_stock():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    ticker = data.get('ticker', '').upper().strip()
    name = data.get('name', '').strip()
    sector = data.get('sector', '').strip()
    price = data.get('price')
    shares_outstanding = data.get('shares_outstanding')
    
    if not ticker or not name or not price:
        return jsonify({'error': 'Ticker, name, and price are required'}), 400
    
    try:
        price = Decimal(str(price))
        if price <= 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid price format'}), 400
    
    if shares_outstanding:
        try:
            shares_outstanding = int(shares_outstanding)
            if shares_outstanding <= 0:
                raise ValueError("Shares outstanding must be positive")
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid shares outstanding format'}), 400
    
    if Stock.query.filter_by(ticker=ticker).first():
        return jsonify({'error': f'Stock with ticker {ticker} already exists'}), 400
    
    stock = Stock(
        ticker=ticker,
        name=name,
        sector=sector,
        price=price,
        shares_outstanding=shares_outstanding
    )
    
    db.session.add(stock)
    db.session.commit()
    
    return jsonify({
        'message': 'Stock created successfully',
        'stock': stock.to_dict()
    }), 201

@bp.route('/stocks/<ticker>', methods=['GET'])
def get_stock(ticker):
    stock = Stock.query.filter_by(ticker=ticker).first()
    
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    return jsonify({'stock': stock.to_dict()})

@bp.route('/stocks/<ticker>', methods=['PUT'])
@login_required
def update_stock(ticker):
    stock = Stock.query.filter_by(ticker=ticker).first()
    
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    name = data.get('name', '').strip()
    sector = data.get('sector', '').strip()
    price = data.get('price')
    shares_outstanding = data.get('shares_outstanding')
    
    if not name or not price:
        return jsonify({'error': 'Name and price are required'}), 400
    
    try:
        price = Decimal(str(price))
        if price <= 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid price format'}), 400
    
    if shares_outstanding:
        try:
            shares_outstanding = int(shares_outstanding)
            if shares_outstanding <= 0:
                raise ValueError("Shares outstanding must be positive")
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid shares outstanding format'}), 400
    
    stock.name = name
    stock.sector = sector
    stock.price = price
    stock.shares_outstanding = shares_outstanding
    
    db.session.commit()
    
    return jsonify({
        'message': 'Stock updated successfully',
        'stock': stock.to_dict()
    })

@bp.route('/stocks/<ticker>', methods=['DELETE'])
@login_required
def delete_stock(ticker):
    stock = Stock.query.filter_by(ticker=ticker).first()
    
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    if stock.trades.count() > 0:
        return jsonify({'error': f'Cannot delete stock {ticker} because it has associated trades'}), 400
    
    db.session.delete(stock)
    db.session.commit()
    
    return jsonify({'message': 'Stock deleted successfully'})

@bp.route('/trades', methods=['GET'])
@login_required
def get_trades():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'trades': [trade.to_dict() for trade in trades.items],
        'total': trades.total,
        'pages': trades.pages,
        'current_page': trades.page,
        'per_page': trades.per_page
    })

@bp.route('/trades', methods=['POST'])
@login_required
def create_trade():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    ticker = data.get('ticker', '').upper().strip()
    side = data.get('side', '').lower().strip()
    quantity = data.get('quantity')
    price = data.get('price')
    
    if not ticker or not side or not quantity or not price:
        return jsonify({'error': 'All fields are required'}), 400
    
    if side not in ['buy', 'sell']:
        return jsonify({'error': 'Side must be either "buy" or "sell"'}), 400
    
    stock = Stock.query.filter_by(ticker=ticker).first()
    if not stock:
        return jsonify({'error': f'Stock with ticker {ticker} not found'}), 400
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity format'}), 400
    
    try:
        price = Decimal(str(price))
        if price <= 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid price format'}), 400
    
    # Check if user has enough shares for sell orders
    if side == 'sell':
        user_shares = 0
        user_trades = Trade.query.filter_by(user_id=current_user.id, stock_id=stock.id).all()
        for trade in user_trades:
            if trade.side == 'buy':
                user_shares += trade.quantity
            else:
                user_shares -= trade.quantity
        
        if user_shares < quantity:
            return jsonify({'error': f'Insufficient shares. You have {user_shares} shares of {ticker}'}), 400
    
    trade = Trade(
        user_id=current_user.id,
        stock_id=stock.id,
        side=side,
        quantity=quantity,
        price=price
    )
    
    db.session.add(trade)
    db.session.commit()
    
    return jsonify({
        'message': 'Trade created successfully',
        'trade': trade.to_dict()
    }), 201

@bp.route('/portfolio', methods=['GET'])
@login_required
def get_portfolio():
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
