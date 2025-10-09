from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import User, Stock, Trade, ChatMessage
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.stocks import bp as stocks_bp
    app.register_blueprint(stocks_bp, url_prefix='/stocks')
    
    from app.trades import bp as trades_bp
    app.register_blueprint(trades_bp, url_prefix='/trades')
    
    from app.portfolio import bp as portfolio_bp
    app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.chat import bp as chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')

    return app
