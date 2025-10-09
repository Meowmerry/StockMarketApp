from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.admin import bp
from app.utils import simulate_price_changes, simulate_market_crash, simulate_market_rally
from app.models import Stock

@bp.route('/simulate')
@login_required
def simulate():
    """Price simulation interface"""
    stocks = Stock.query.limit(10).all()  # Show recent stocks for context
    return render_template('admin/simulate.html', stocks=stocks)

@bp.route('/simulate/random', methods=['POST'])
@login_required
def simulate_random():
    """Simulate random price changes"""
    data = request.get_json() if request.is_json else request.form
    
    volatility = float(data.get('volatility', 0.02))  # Default 2%
    max_stocks = int(data.get('max_stocks', 0)) if data.get('max_stocks') else None
    
    if volatility <= 0 or volatility > 1:
        error_msg = 'Volatility must be between 0 and 1 (0% to 100%)'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('admin.simulate'))
    
    result = simulate_price_changes(volatility=volatility, max_stocks=max_stocks)
    
    if request.is_json:
        return jsonify({
            'message': f'Simulated price changes for {result["updated_count"]} stocks',
            'result': result
        }), 200
    
    flash(f'Simulated price changes for {result["updated_count"]} stocks', 'success')
    return redirect(url_for('admin.simulate'))

@bp.route('/simulate/crash', methods=['POST'])
@login_required
def simulate_crash():
    """Simulate market crash"""
    data = request.get_json() if request.is_json else request.form
    
    crash_percent = float(data.get('crash_percent', 0.15))  # Default 15%
    
    if crash_percent <= 0 or crash_percent > 1:
        error_msg = 'Crash percentage must be between 0 and 1 (0% to 100%)'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('admin.simulate'))
    
    result = simulate_market_crash(crash_percent=crash_percent)
    
    if request.is_json:
        return jsonify({
            'message': f'Market crash simulated: {crash_percent*100:.1f}% drop for {result["updated_count"]} stocks',
            'result': result
        }), 200
    
    flash(f'Market crash simulated: {crash_percent*100:.1f}% drop for {result["updated_count"]} stocks', 'warning')
    return redirect(url_for('admin.simulate'))

@bp.route('/simulate/rally', methods=['POST'])
@login_required
def simulate_rally():
    """Simulate market rally"""
    data = request.get_json() if request.is_json else request.form
    
    rally_percent = float(data.get('rally_percent', 0.10))  # Default 10%
    
    if rally_percent <= 0 or rally_percent > 1:
        error_msg = 'Rally percentage must be between 0 and 1 (0% to 100%)'
        if request.is_json:
            return jsonify({'error': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('admin.simulate'))
    
    result = simulate_market_rally(rally_percent=rally_percent)
    
    if request.is_json:
        return jsonify({
            'message': f'Market rally simulated: {rally_percent*100:.1f}% gain for {result["updated_count"]} stocks',
            'result': result
        }), 200
    
    flash(f'Market rally simulated: {rally_percent*100:.1f}% gain for {result["updated_count"]} stocks', 'success')
    return redirect(url_for('admin.simulate'))
