"""
Chat routes for the AI chatbot feature.
Handles chat API endpoints and chat page rendering.
"""

import uuid
from flask import request, jsonify, render_template, session
from flask_login import current_user
from app.chat import bp
from app import db
from app.models import ChatMessage, Stock, Trade
from app.chat_service import get_chat_service
from sqlalchemy import func, desc


@bp.route('/chat')
def chat_page():
    """Render the chat page"""
    # Generate session ID for conversation tracking
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())

    return render_template('chat/index.html')


@bp.route('/chat/api', methods=['POST'])
def chat_api():
    """
    Main chat API endpoint.
    Receives user messages and returns AI responses.
    """
    try:
        # Get request data
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required'
            }), 400

        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty'
            }), 400

        # Limit message length
        if len(user_message) > 1000:
            return jsonify({
                'error': 'Message is too long (max 1000 characters)'
            }), 400

        # Get or create session ID
        if 'chat_session_id' not in session:
            session['chat_session_id'] = str(uuid.uuid4())

        session_id = session['chat_session_id']

        # Get conversation history (last 10 messages)
        history = ChatMessage.query.filter_by(
            session_id=session_id
        ).order_by(desc(ChatMessage.timestamp)).limit(10).all()

        # Reverse to get chronological order
        history = [msg.to_dict() for msg in reversed(history)]

        # Get user context if logged in
        user_context = None
        if current_user.is_authenticated:
            user_context = _get_user_context(current_user.id)

        # Get AI response
        chat_service = get_chat_service()
        result = chat_service.get_response(
            user_message=user_message,
            conversation_history=history,
            user_context=user_context
        )

        # Save user message to database
        user_msg = ChatMessage(
            user_id=current_user.id if current_user.is_authenticated else None,
            session_id=session_id,
            role='user',
            content=user_message
        )
        db.session.add(user_msg)

        # Save assistant response to database
        assistant_msg = ChatMessage(
            user_id=current_user.id if current_user.is_authenticated else None,
            session_id=session_id,
            role='assistant',
            content=result['response']
        )
        db.session.add(assistant_msg)

        db.session.commit()

        return jsonify({
            'response': result['response'],
            'success': result['success'],
            'timestamp': assistant_msg.timestamp.isoformat()
        })

    except Exception as e:
        print(f"Error in chat API: {e}")
        db.session.rollback()
        return jsonify({
            'error': 'An error occurred while processing your message',
            'response': 'I apologize, but I encountered an error. Please try again.'
        }), 500


@bp.route('/chat/history', methods=['GET'])
def chat_history():
    """Get chat history for the current session"""
    try:
        # Get session ID
        session_id = session.get('chat_session_id')
        if not session_id:
            return jsonify({'messages': []})

        # Get messages
        messages = ChatMessage.query.filter_by(
            session_id=session_id
        ).order_by(ChatMessage.timestamp).limit(50).all()

        return jsonify({
            'messages': [msg.to_dict() for msg in messages]
        })

    except Exception as e:
        print(f"Error getting chat history: {e}")
        return jsonify({'error': 'Failed to load chat history'}), 500


@bp.route('/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history for the current session"""
    try:
        # Generate new session ID
        session['chat_session_id'] = str(uuid.uuid4())

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error clearing chat: {e}")
        return jsonify({'error': 'Failed to clear chat'}), 500


def _get_user_context(user_id: int) -> dict:
    """
    Gather user context for providing personalized responses.

    Args:
        user_id: The user's ID

    Returns:
        Dictionary with portfolio, holdings, and stock data
    """
    context = {}

    # Get available stocks
    stocks = Stock.query.all()
    context['available_stocks'] = [
        {
            'ticker': s.ticker,
            'name': s.name,
            'price': float(s.price),
            'sector': s.sector
        }
        for s in stocks
    ]

    # Get user's recent trades
    recent_trades = Trade.query.filter_by(
        user_id=user_id
    ).order_by(desc(Trade.timestamp)).limit(10).all()

    context['recent_trades'] = [
        {
            'ticker': t.stock.ticker,
            'side': t.side,
            'quantity': t.quantity,
            'price': float(t.price),
            'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M')
        }
        for t in recent_trades
    ]

    # Calculate portfolio summary
    holdings_query = db.session.query(
        Stock.ticker,
        Stock.name,
        Stock.price,
        func.sum(
            func.case(
                (Trade.side == 'buy', Trade.quantity),
                else_=-Trade.quantity
            )
        ).label('quantity'),
        func.avg(Trade.price).label('avg_price')
    ).join(Trade).filter(
        Trade.user_id == user_id
    ).group_by(
        Stock.id, Stock.ticker, Stock.name, Stock.price
    ).having(
        func.sum(
            func.case(
                (Trade.side == 'buy', Trade.quantity),
                else_=-Trade.quantity
            )
        ) > 0
    ).all()

    holdings = []
    total_value = 0

    for holding in holdings_query:
        quantity = int(holding.quantity)
        current_price = float(holding.price)
        avg_price = float(holding.avg_price)
        value = quantity * current_price

        holdings.append({
            'ticker': holding.ticker,
            'name': holding.name,
            'quantity': quantity,
            'current_price': current_price,
            'avg_price': avg_price,
            'value': value
        })
        total_value += value

    context['portfolio'] = {
        'holdings': holdings,
        'holdings_count': len(holdings),
        'total_value': total_value
    }

    return context
