import pytest
from decimal import Decimal
from app import db
from app.models import User, Stock, Trade

@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def user(app):
    """Create a test user."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def stock(app):
    """Create a test stock."""
    stock = Stock(
        ticker='AAPL',
        name='Apple Inc.',
        sector='Technology',
        price=Decimal('150.00'),
        shares_outstanding=15500000000
    )
    db.session.add(stock)
    db.session.commit()
    return stock

class TestTrades:
    """Test trade functionality."""
    
    def test_create_buy_trade(self, client, user, stock):
        """Test creating a buy trade."""
        # Login first
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/trades/create', data={
            'ticker': 'AAPL',
            'side': 'buy',
            'quantity': '100',
            'price': '150.00'
        })
        
        # Should redirect after successful creation
        assert response.status_code == 302
        
        # Check that trade was created
        trade = Trade.query.filter_by(user_id=user.id, stock_id=stock.id).first()
        assert trade is not None
        assert trade.side == 'buy'
        assert trade.quantity == 100
        assert trade.price == Decimal('150.00')
    
    def test_create_sell_trade_with_sufficient_shares(self, client, user, stock):
        """Test creating a sell trade when user has sufficient shares."""
        # First create a buy trade
        buy_trade = Trade(
            user_id=user.id,
            stock_id=stock.id,
            side='buy',
            quantity=100,
            price=Decimal('150.00')
        )
        db.session.add(buy_trade)
        db.session.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Now create a sell trade
        response = client.post('/trades/create', data={
            'ticker': 'AAPL',
            'side': 'sell',
            'quantity': '50',
            'price': '155.00'
        })
        
        # Should redirect after successful creation
        assert response.status_code == 302
        
        # Check that sell trade was created
        sell_trade = Trade.query.filter_by(
            user_id=user.id, 
            stock_id=stock.id, 
            side='sell'
        ).first()
        assert sell_trade is not None
        assert sell_trade.quantity == 50
    
    def test_create_sell_trade_insufficient_shares(self, client, user, stock):
        """Test creating a sell trade when user has insufficient shares."""
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Try to sell without owning any shares
        response = client.post('/trades/create', data={
            'ticker': 'AAPL',
            'side': 'sell',
            'quantity': '100',
            'price': '150.00'
        })
        
        assert response.status_code == 200  # Should stay on create page
        assert b'Insufficient shares' in response.data
    
    def test_create_trade_invalid_side(self, client, user, stock):
        """Test creating trade with invalid side."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/trades/create', data={
            'ticker': 'AAPL',
            'side': 'invalid',
            'quantity': '100',
            'price': '150.00'
        })
        
        assert response.status_code == 200  # Should stay on create page
        assert b'Side must be either "buy" or "sell"' in response.data
    
    def test_create_trade_invalid_quantity(self, client, user, stock):
        """Test creating trade with invalid quantity."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/trades/create', data={
            'ticker': 'AAPL',
            'side': 'buy',
            'quantity': '0',  # Invalid quantity
            'price': '150.00'
        })
        
        assert response.status_code == 200  # Should stay on create page
        assert b'Invalid quantity format' in response.data
    
    def test_create_trade_invalid_price(self, client, user, stock):
        """Test creating trade with invalid price."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/trades/create', data={
            'ticker': 'AAPL',
            'side': 'buy',
            'quantity': '100',
            'price': '-10.00'  # Negative price
        })
        
        assert response.status_code == 200  # Should stay on create page
        assert b'Invalid price format' in response.data
    
    def test_trades_list(self, client, user, stock):
        """Test trades list page."""
        # Create a trade first
        trade = Trade(
            user_id=user.id,
            stock_id=stock.id,
            side='buy',
            quantity=100,
            price=Decimal('150.00')
        )
        db.session.add(trade)
        db.session.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.get('/trades/')
        assert response.status_code == 200
        assert b'AAPL' in response.data
        assert b'BUY' in response.data
    
    def test_trade_detail(self, client, user, stock):
        """Test trade detail page."""
        # Create a trade first
        trade = Trade(
            user_id=user.id,
            stock_id=stock.id,
            side='buy',
            quantity=100,
            price=Decimal('150.00')
        )
        db.session.add(trade)
        db.session.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.get(f'/trades/{trade.id}')
        assert response.status_code == 200
        assert b'AAPL' in response.data
        assert b'BUY' in response.data
        assert b'150.00' in response.data
    
    def test_edit_trade(self, client, user, stock):
        """Test editing a trade."""
        # Create a trade first
        trade = Trade(
            user_id=user.id,
            stock_id=stock.id,
            side='buy',
            quantity=100,
            price=Decimal('150.00')
        )
        db.session.add(trade)
        db.session.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post(f'/trades/{trade.id}/edit', data={
            'side': 'buy',
            'quantity': '150',
            'price': '155.00'
        })
        
        # Should redirect after successful update
        assert response.status_code == 302
        
        # Check that trade was updated
        updated_trade = Trade.query.get(trade.id)
        assert updated_trade.quantity == 150
        assert updated_trade.price == Decimal('155.00')
    
    def test_delete_trade(self, client, user, stock):
        """Test deleting a trade."""
        # Create a trade first
        trade = Trade(
            user_id=user.id,
            stock_id=stock.id,
            side='buy',
            quantity=100,
            price=Decimal('150.00')
        )
        db.session.add(trade)
        db.session.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post(f'/trades/{trade.id}/delete')
        
        # Should redirect after successful deletion
        assert response.status_code == 302
        
        # Check that trade was deleted
        deleted_trade = Trade.query.get(trade.id)
        assert deleted_trade is None
    
    def test_api_get_trades(self, client, user, stock):
        """Test API to get trades."""
        # Create a trade first
        trade = Trade(
            user_id=user.id,
            stock_id=stock.id,
            side='buy',
            quantity=100,
            price=Decimal('150.00')
        )
        db.session.add(trade)
        db.session.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.get('/api/trades')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'trades' in data
        assert len(data['trades']) == 1
        assert data['trades'][0]['side'] == 'buy'
    
    def test_api_create_trade(self, client, user, stock):
        """Test API to create trade."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/api/trades', json={
            'ticker': 'AAPL',
            'side': 'buy',
            'quantity': 100,
            'price': 150.00
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Trade created successfully'
        assert data['trade']['side'] == 'buy'
        
        # Check that trade was created
        trade = Trade.query.filter_by(user_id=user.id, stock_id=stock.id).first()
        assert trade is not None
