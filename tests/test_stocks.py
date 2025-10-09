import pytest
from decimal import Decimal
from app import db
from app.models import User, Stock

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

class TestStocks:
    """Test stock functionality."""
    
    def test_create_stock(self, client, user):
        """Test creating a new stock."""
        # Login first
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/stocks/create', data={
            'ticker': 'GOOGL',
            'name': 'Alphabet Inc.',
            'sector': 'Technology',
            'price': '142.50',
            'shares_outstanding': '12600000000'
        })
        
        # Should redirect after successful creation
        assert response.status_code == 302
        
        # Check that stock was created
        stock = Stock.query.filter_by(ticker='GOOGL').first()
        assert stock is not None
        assert stock.name == 'Alphabet Inc.'
        assert stock.price == Decimal('142.50')
        assert stock.shares_outstanding == 12600000000
    
    def test_create_stock_duplicate_ticker(self, client, user, stock):
        """Test creating stock with duplicate ticker."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/stocks/create', data={
            'ticker': 'AAPL',  # Same as existing stock
            'name': 'Different Apple',
            'sector': 'Technology',
            'price': '150.00'
        })
        
        assert response.status_code == 200  # Should stay on create page
        assert b'Stock with ticker AAPL already exists' in response.data
    
    def test_create_stock_invalid_price(self, client, user):
        """Test creating stock with invalid price."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/stocks/create', data={
            'ticker': 'INVALID',
            'name': 'Invalid Stock',
            'price': '-10.00'  # Negative price
        })
        
        assert response.status_code == 200  # Should stay on create page
        assert b'Invalid price format' in response.data
    
    def test_stocks_list(self, client, stock):
        """Test stocks list page."""
        response = client.get('/stocks/')
        assert response.status_code == 200
        assert b'AAPL' in response.data
        assert b'Apple Inc.' in response.data
    
    def test_stock_detail(self, client, stock):
        """Test stock detail page."""
        response = client.get(f'/stocks/{stock.ticker}')
        assert response.status_code == 200
        assert b'AAPL' in response.data
        assert b'Apple Inc.' in response.data
        assert b'150.00' in response.data
    
    def test_edit_stock(self, client, user, stock):
        """Test editing a stock."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post(f'/stocks/{stock.ticker}/edit', data={
            'name': 'Apple Inc. Updated',
            'sector': 'Consumer Technology',
            'price': '155.00',
            'shares_outstanding': '15500000000'
        })
        
        # Should redirect after successful update
        assert response.status_code == 302
        
        # Check that stock was updated
        updated_stock = Stock.query.filter_by(ticker='AAPL').first()
        assert updated_stock.name == 'Apple Inc. Updated'
        assert updated_stock.price == Decimal('155.00')
    
    def test_delete_stock(self, client, user):
        """Test deleting a stock."""
        # Create a stock first
        test_stock = Stock(
            ticker='TEST',
            name='Test Stock',
            price=Decimal('100.00')
        )
        db.session.add(test_stock)
        db.session.commit()
        
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post(f'/stocks/{test_stock.ticker}/delete')
        
        # Should redirect after successful deletion
        assert response.status_code == 302
        
        # Check that stock was deleted
        deleted_stock = Stock.query.filter_by(ticker='TEST').first()
        assert deleted_stock is None
    
    def test_api_get_stocks(self, client, stock):
        """Test API to get stocks."""
        response = client.get('/api/stocks')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'stocks' in data
        assert len(data['stocks']) == 1
        assert data['stocks'][0]['ticker'] == 'AAPL'
    
    def test_api_create_stock(self, client, user):
        """Test API to create stock."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.post('/api/stocks', json={
            'ticker': 'MSFT',
            'name': 'Microsoft Corporation',
            'sector': 'Technology',
            'price': 378.85,
            'shares_outstanding': 7420000000
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Stock created successfully'
        assert data['stock']['ticker'] == 'MSFT'
        
        # Check that stock was created
        stock = Stock.query.filter_by(ticker='MSFT').first()
        assert stock is not None
    
    def test_api_get_stock(self, client, stock):
        """Test API to get specific stock."""
        response = client.get(f'/api/stocks/{stock.ticker}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['stock']['ticker'] == 'AAPL'
        assert data['stock']['name'] == 'Apple Inc.'
    
    def test_api_update_stock(self, client, user, stock):
        """Test API to update stock."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.put(f'/api/stocks/{stock.ticker}', json={
            'name': 'Apple Inc. Updated',
            'sector': 'Consumer Technology',
            'price': 155.00,
            'shares_outstanding': 15500000000
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Stock updated successfully'
        assert data['stock']['name'] == 'Apple Inc. Updated'
    
    def test_api_delete_stock(self, client, user):
        """Test API to delete stock."""
        # Create a stock first
        test_stock = Stock(
            ticker='TEST',
            name='Test Stock',
            price=Decimal('100.00')
        )
        db.session.add(test_stock)
        db.session.commit()
        
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.delete(f'/api/stocks/{test_stock.ticker}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['message'] == 'Stock deleted successfully'
        
        # Check that stock was deleted
        deleted_stock = Stock.query.filter_by(ticker='TEST').first()
        assert deleted_stock is None
