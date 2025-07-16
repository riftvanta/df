from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap5
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
bootstrap = Bootstrap5()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    
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
    from app.routes import auth
    app.register_blueprint(auth.bp)
    
    # Add root route
    @app.route('/')
    def index():
        return auth.index()
    
    # Placeholder routes for admin and employee (will be implemented in Phase 4)
    from flask import Blueprint, render_template_string, redirect, url_for
    from flask_login import login_required, current_user
    
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
    employee_bp = Blueprint('employee', __name__, url_prefix='/employee')
    
    @admin_bp.route('/dashboard')
    @login_required
    def dashboard():
        if not current_user.is_admin:
            return redirect(url_for('employee.dashboard'))
        return render_template_string('''
            <h1>Admin Dashboard</h1>
            <p>Welcome, {{ current_user.username }}!</p>
            <p>This is a placeholder for the admin dashboard.</p>
            <a href="{{ url_for('auth.logout') }}" class="btn btn-danger">Logout</a>
        ''')
    
    @admin_bp.route('/projects')
    @login_required
    def projects():
        return render_template_string('<h1>Projects (Coming Soon)</h1>')
    
    @admin_bp.route('/employees')
    @login_required
    def employees():
        return render_template_string('<h1>Employees (Coming Soon)</h1>')
    
    @admin_bp.route('/reports')
    @login_required 
    def reports():
        return render_template_string('<h1>Reports (Coming Soon)</h1>')
    
    @employee_bp.route('/dashboard') 
    @login_required
    def dashboard():
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return render_template_string('''
            <h1>Employee Dashboard</h1>
            <p>Welcome, {{ current_user.username }}!</p>
            <p>This is a placeholder for the employee dashboard.</p>
            <a href="{{ url_for('auth.logout') }}" class="btn btn-danger">Logout</a>
        ''')
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(employee_bp)
    
    return app 