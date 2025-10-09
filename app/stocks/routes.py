from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Stock
from app.stocks import bp
from decimal import Decimal

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    stocks = Stock.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('stocks/index.html', stocks=stocks)

@bp.route('/<ticker>')
def detail(ticker):
    stock = Stock.query.filter_by(ticker=ticker).first_or_404()
    return render_template('stocks/detail.html', stock=stock)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        ticker = data.get('ticker', '').upper().strip()
        name = data.get('name', '').strip()
        sector = data.get('sector', '').strip()
        price = data.get('price')
        shares_outstanding = data.get('shares_outstanding')
        
        # Validation
        if not ticker or not name or not price:
            error_msg = 'Ticker, name, and price are required.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('stocks/create.html')
        
        try:
            price = Decimal(str(price))
            if price <= 0:
                raise ValueError("Price must be positive")
        except (ValueError, TypeError):
            error_msg = 'Invalid price format.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('stocks/create.html')
        
        if shares_outstanding:
            try:
                shares_outstanding = int(shares_outstanding)
                if shares_outstanding <= 0:
                    raise ValueError("Shares outstanding must be positive")
            except (ValueError, TypeError):
                error_msg = 'Invalid shares outstanding format.'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('stocks/create.html')
        
        # Check if ticker already exists
        if Stock.query.filter_by(ticker=ticker).first():
            error_msg = f'Stock with ticker {ticker} already exists.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('stocks/create.html')
        
        stock = Stock(
            ticker=ticker,
            name=name,
            sector=sector,
            price=price,
            shares_outstanding=shares_outstanding
        )
        
        db.session.add(stock)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Stock created successfully', 'stock': stock.to_dict()}), 201
        
        flash(f'Stock {ticker} created successfully!', 'success')
        return redirect(url_for('stocks.detail', ticker=ticker))
    
    return render_template('stocks/create.html')

@bp.route('/<ticker>/edit', methods=['GET', 'POST'])
@login_required
def edit(ticker):
    stock = Stock.query.filter_by(ticker=ticker).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name', '').strip()
        sector = data.get('sector', '').strip()
        price = data.get('price')
        shares_outstanding = data.get('shares_outstanding')
        
        # Validation
        if not name or not price:
            error_msg = 'Name and price are required.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('stocks/edit.html', stock=stock)
        
        try:
            price = Decimal(str(price))
            if price <= 0:
                raise ValueError("Price must be positive")
        except (ValueError, TypeError):
            error_msg = 'Invalid price format.'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('stocks/edit.html', stock=stock)
        
        if shares_outstanding:
            try:
                shares_outstanding = int(shares_outstanding)
                if shares_outstanding <= 0:
                    raise ValueError("Shares outstanding must be positive")
            except (ValueError, TypeError):
                error_msg = 'Invalid shares outstanding format.'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('stocks/edit.html', stock=stock)
        
        stock.name = name
        stock.sector = sector
        stock.price = price
        stock.shares_outstanding = shares_outstanding
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Stock updated successfully', 'stock': stock.to_dict()}), 200
        
        flash(f'Stock {ticker} updated successfully!', 'success')
        return redirect(url_for('stocks.detail', ticker=ticker))
    
    return render_template('stocks/edit.html', stock=stock)

@bp.route('/<ticker>/delete', methods=['POST'])
@login_required
def delete(ticker):
    stock = Stock.query.filter_by(ticker=ticker).first_or_404()
    
    # Check if there are any trades for this stock
    if stock.trades.count() > 0:
        error_msg = f'Cannot delete stock {ticker} because it has associated trades.'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('stocks.detail', ticker=ticker))
    
    db.session.delete(stock)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': 'Stock deleted successfully'}), 200
    
    flash(f'Stock {ticker} deleted successfully!', 'success')
    return redirect(url_for('stocks.index'))
