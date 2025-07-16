from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap4
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
bootstrap = Bootstrap4()

def create_app():
    app = Flask(__name__)
    
    # Load configuration based on environment
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL'):
        app.config.from_object('config.ProductionConfig')
        print("Loading ProductionConfig for Railway deployment")
    else:
        app.config.from_object('config.DevelopmentConfig')
        print("Loading DevelopmentConfig for local development")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    bootstrap.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    from app.routes import auth, admin, employee, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(employee.bp)
    app.register_blueprint(api.bp)
    
    # Add root route
    @app.route('/')
    def index():
        return auth.index()
    
    # Health check endpoint for Railway
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'app': 'Manufacturing Workload Manager'}, 200
    
    return app 