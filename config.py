import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration
    # Get DATABASE_URL from environment (Render provides this automatically)
    database_url = os.environ.get('DATABASE_URL')

    # Fix for Render's postgres:// vs postgresql:// URL format
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///stock_market.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

class DevelopmentConfig(Config):
    """Development configuration - uses local PostgreSQL or SQLite"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration - uses PostgreSQL"""
    DEBUG = False
    TESTING = False
    # Ensure SECRET_KEY is set in production
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production")
