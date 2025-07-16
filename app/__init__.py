from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap4
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
bootstrap = Bootstrap4()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration based on environment
    if config_name:
        from config import config
        app.config.from_object(config[config_name])
    elif os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL'):
        app.config.from_object('config.ProductionConfig')
        print("Loading ProductionConfig for Railway deployment")
    else:
        app.config.from_object('config.DevelopmentConfig')
        print("Loading DevelopmentConfig for local development")
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    bootstrap.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Initialize security (Talisman) for production
    if not app.debug:
        talisman.init_app(app, 
            force_https=False,  # Railway handles HTTPS termination
            strict_transport_security=True,
            content_security_policy={
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                'img-src': "'self' data: https:",
                'font-src': "'self' https://cdn.jsdelivr.net",
            }
        )
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    from app.routes import auth, admin, employee, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(employee.bp)
    app.register_blueprint(api.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add context processors
    register_context_processors(app)
    
    # Add root route
    @app.route('/')
    def index():
        return auth.index()
    
    # Health check endpoint for Railway
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'app': 'Manufacturing Workload Manager'}, 200
    
    # Database initialization check for Railway
    @app.before_first_request
    def init_database():
        """Initialize database schema if running on Railway"""
        if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL'):
            try:
                from sqlalchemy import text
                # Quick check if original_hours column exists
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'assignments' AND column_name = 'original_hours'
                """))
                
                if not result.fetchone():
                    print("⚠️  Database schema incomplete, running initialization...")
                    import subprocess
                    subprocess.run([sys.executable, 'railway_init.py'], check=True)
                    print("✅ Database initialization completed via fallback")
                else:
                    print("✅ Database schema check passed")
                    
            except Exception as init_error:
                print(f"⚠️  Database initialization check failed: {init_error}")
                # Don't crash the app, just log the error
    
    return app

def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configure file handler
        file_handler = RotatingFileHandler('logs/manufacturing_app.log', 
                                         maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        
        # Set log level from config
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(log_level)
        app.logger.info('Manufacturing App startup')

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden'}, 403
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'error': 'Rate limit exceeded', 'retry_after': e.retry_after}, 429
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return {'error': 'CSRF token missing or invalid'}, 400

def register_context_processors(app):
    """Register context processors for templates"""
    
    @app.context_processor
    def inject_config():
        return {
            'ITEMS_PER_PAGE': app.config.get('ITEMS_PER_PAGE', 20),
            'app_name': 'Manufacturing Workload Manager'
        }
    
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

# Import for error handling
from flask_wtf.csrf import CSRFError 