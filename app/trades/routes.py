from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Stock, Trade
from app.trades import bp
from decimal import Decimal
from datetime import datetime

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('trades/index.html', trades=trades)

@bp.route('/<int:trade_id>')
@login_required
def detail(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first_or_404()
    return render_template('trades/detail.html', trade=trade)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        ticker = data.get('ticker', '').upper().strip()
        side = data.get('side', '').lower().strip()
        quantity = data.get('quantity')
        price = data.get('price')
        
        # Validation
        if not ticker or not side or not quantity or not price:
            error_msg = 'All fields are required.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/create.html', stocks=Stock.query.all())
        
        if side not in ['buy', 'sell']:
            error_msg = 'Side must be either "buy" or "sell".'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/create.html', stocks=Stock.query.all())
        
        # Check if stock exists
        stock = Stock.query.filter_by(ticker=ticker).first()
        if not stock:
            error_msg = f'Stock with ticker {ticker} not found.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/create.html', stocks=Stock.query.all())
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except (ValueError, TypeError):
            error_msg = 'Invalid quantity format.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/create.html', stocks=Stock.query.all())
        
        try:
            price = Decimal(str(price))
            if price <= 0:
                raise ValueError("Price must be positive")
        except (ValueError, TypeError):
            error_msg = 'Invalid price format.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/create.html', stocks=Stock.query.all())
        
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
                error_msg = f'Insufficient shares. You have {user_shares} shares of {ticker}.'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('trades/create.html', stocks=Stock.query.all())
        
        trade = Trade(
            user_id=current_user.id,
            stock_id=stock.id,
            side=side,
            quantity=quantity,
            price=price
        )
        
        db.session.add(trade)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Trade created successfully', 'trade': trade.to_dict()}), 201
        
        flash(f'Trade executed successfully! {side.upper()} {quantity} {ticker} @ ${price}', 'success')
        return redirect(url_for('trades.index'))
    
    stocks = Stock.query.all()
    return render_template('trades/create.html', stocks=stocks)

@bp.route('/<int:trade_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        side = data.get('side', '').lower().strip()
        quantity = data.get('quantity')
        price = data.get('price')
        
        # Validation
        if not side or not quantity or not price:
            error_msg = 'All fields are required.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/edit.html', trade=trade)
        
        if side not in ['buy', 'sell']:
            error_msg = 'Side must be either "buy" or "sell".'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/edit.html', trade=trade)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except (ValueError, TypeError):
            error_msg = 'Invalid quantity format.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/edit.html', trade=trade)
        
        try:
            price = Decimal(str(price))
            if price <= 0:
                raise ValueError("Price must be positive")
        except (ValueError, TypeError):
            error_msg = 'Invalid price format.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('trades/edit.html', trade=trade)
        
        # Check if user has enough shares for sell orders
        if side == 'sell':
            user_shares = 0
            user_trades = Trade.query.filter_by(user_id=current_user.id, stock_id=trade.stock_id).filter(Trade.id != trade_id).all()
            for user_trade in user_trades:
                if user_trade.side == 'buy':
                    user_shares += user_trade.quantity
                else:
                    user_shares -= user_trade.quantity
            
            if user_shares < quantity:
                error_msg = f'Insufficient shares. You have {user_shares} shares of {trade.stock.ticker}.'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('trades/edit.html', trade=trade)
        
        trade.side = side
        trade.quantity = quantity
        trade.price = price
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Trade updated successfully', 'trade': trade.to_dict()}), 200
        
        flash(f'Trade updated successfully!', 'success')
        return redirect(url_for('trades.detail', trade_id=trade.id))
    
    return render_template('trades/edit.html', trade=trade)

@bp.route('/<int:trade_id>/delete', methods=['POST'])
@login_required
def delete(trade_id):
    trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(trade)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': 'Trade deleted successfully'}), 200
    
    flash(f'Trade deleted successfully!', 'success')
    return redirect(url_for('trades.index'))
