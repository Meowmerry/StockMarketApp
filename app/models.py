from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with trades
    trades = db.relationship('Trade', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), index=True, unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    sector = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    shares_outstanding = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with trades
    trades = db.relationship('Trade', backref='stock', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'name': self.name,
            'sector': self.sector,
            'price': float(self.price),
            'shares_outstanding': self.shares_outstanding,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Stock {self.ticker}: {self.name}>'

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    side = db.Column(db.String(4), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stock_id': self.stock_id,
            'ticker': self.stock.ticker,
            'side': self.side,
            'quantity': self.quantity,
            'price': float(self.price),
            'timestamp': self.timestamp.isoformat(),
            'total_value': float(self.quantity * self.price)
        }
    
    def __repr__(self):
        return f'<Trade {self.side} {self.quantity} {self.stock.ticker} @ ${self.price}>'
