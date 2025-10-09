import pytest
from flask import url_for
from app import create_app, db
from app.models import User

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

class TestAuth:
    """Test authentication functionality."""
    
    def test_register_page_loads(self, client):
        """Test that register page loads correctly."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_register_new_user(self, client):
        """Test registering a new user."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        })
        
        # Should redirect after successful registration
        assert response.status_code == 302
        
        # Check that user was created
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.check_password('newpass123')
    
    def test_register_duplicate_username(self, client, user):
        """Test that duplicate usernames are rejected."""
        response = client.post('/auth/register', data={
            'username': 'testuser',  # Same as existing user
            'email': 'different@example.com',
            'password': 'newpass123'
        })
        
        assert response.status_code == 200  # Should stay on register page
        assert b'Username already exists' in response.data
    
    def test_register_duplicate_email(self, client, user):
        """Test that duplicate emails are rejected."""
        response = client.post('/auth/register', data={
            'username': 'differentuser',
            'email': 'test@example.com',  # Same as existing user
            'password': 'newpass123'
        })
        
        assert response.status_code == 200  # Should stay on register page
        assert b'Email already registered' in response.data
    
    def test_login_page_loads(self, client):
        """Test that login page loads correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_valid_credentials(self, client, user):
        """Test login with valid credentials."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Should redirect after successful login
        assert response.status_code == 302
    
    def test_login_invalid_credentials(self, client, user):
        """Test login with invalid credentials."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 200  # Should stay on login page
        assert b'Invalid username or password' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'somepass'
        })
        
        assert response.status_code == 200  # Should stay on login page
        assert b'Invalid username or password' in response.data
    
    def test_logout(self, client, user):
        """Test logout functionality."""
        # First login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Then logout
        response = client.get('/auth/logout')
        assert response.status_code == 302  # Should redirect
    
    def test_api_register(self, client):
        """Test API user registration."""
        response = client.post('/api/register', json={
            'username': 'apiuser',
            'email': 'apiuser@example.com',
            'password': 'apipass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert data['username'] == 'apiuser'
        
        # Check that user was created
        user = User.query.filter_by(username='apiuser').first()
        assert user is not None
    
    def test_api_login(self, client, user):
        """Test API login."""
        response = client.post('/api/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert data['username'] == 'testuser'
