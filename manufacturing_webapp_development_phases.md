# Manufacturing Webapp Development Phases

## Overview
This document outlines the step-by-step development phases for building the Manufacturing Workload Management App using Flask with traditional server-side rendering, SQLite for local development, and PostgreSQL for Railway deployment.

## Phase 1: Project Setup and Initial Configuration

### Step 1.1: Create Project Structure
```bash
# Create project directory
mkdir manufacturing_app
cd manufacturing_app

# Create Flask package structure
mkdir -p app/{routes,templates/{auth,admin,employee},static/{css,js,img}}
mkdir -p app/templates/{layouts,components,includes}
```

### Step 1.2: Initialize Virtual Environment
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### Step 1.3: Create requirements.txt
```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-Migrate==4.0.5
psycopg2-binary==2.9.9
python-dotenv==1.0.0
gunicorn==21.2.0
pandas==2.1.4
bootstrap-flask==2.3.3
```

### Step 1.4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 1.5: Create Configuration Files

**Create .env file:**
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///manufacturing.db
```

**Create .gitignore:**
```
venv/
*.pyc
__pycache__/
instance/
.env
*.db
.DS_Store
```

**Create config.py:**
```python
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'manufacturing.db')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
```

### Step 1.6: Create Application Factory

**Create app/__init__.py:**
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from bootstrap_flask import Bootstrap5
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
    from app.routes import auth, admin, employee, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(employee.bp)
    app.register_blueprint(api.bp)
    
    return app
```

**Create run.py:**
```python
from app import create_app, db
from app.models import User, Project, Assignment, SkillsMatrix, Vacation

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Project': Project,
        'Assignment': Assignment,
        'SkillsMatrix': SkillsMatrix,
        'Vacation': Vacation
    }

if __name__ == '__main__':
    app.run()
```

## Phase 2: Database Models and Migrations

### Step 2.1: Create Database Models

**Create app/models.py:**
```python
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='employee')  # admin or employee
    department_id = db.Column(db.Integer, nullable=False)
    team_id = db.Column(db.Integer, nullable=False)
    hours_per_week = db.Column(db.Float, default=40.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='employee', lazy='dynamic')
    skills = db.relationship('SkillsMatrix', backref='employee', lazy='dynamic')
    vacations = db.relationship('Vacation', backref='employee', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_number = db.Column(db.String(50), unique=True, nullable=False)
    model_type = db.Column(db.String(20), nullable=False)  # PAH, PPH, REF, APS, PSC
    customer_country = db.Column(db.String(50), nullable=False)
    difficulty_level = db.Column(db.Integer)  # 1-5 scale
    estimated_hours = db.Column(db.Float, nullable=False)
    assembly_start_date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='unassigned')
    requires_ref_first = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='project', lazy='dynamic')

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, on_hold, completed
    hours_remaining = db.Column(db.Float)
    hold_reason = db.Column(db.String(100))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_status_change = db.Column(db.DateTime, default=datetime.utcnow)

class SkillsMatrix(db.Model):
    __tablename__ = 'skills_matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    machine_type = db.Column(db.String(20), nullable=False)  # PAH, PPH, REF
    skill_level = db.Column(db.String(20), nullable=False)  # primary, secondary
    efficiency_factor = db.Column(db.Float, default=1.0)

class Vacation(db.Model):
    __tablename__ = 'vacations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Step 2.2: Initialize Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Step 2.3: Create Seed Data Script
**Create seed_data.py:**
```python
from app import create_app, db
from app.models import User, SkillsMatrix
from datetime import datetime

def seed_database():
    app = create_app()
    with app.app_context():
        # Create admin user
        admin = User(
            email='admin@manufacturing.com',
            username='admin',
            role='admin',
            department_id=1,
            team_id=1
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create sample employees
        # Add more employees here...
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
```

## Phase 3: Authentication System

### Step 3.1: Create Authentication Forms

**Create app/forms.py:**
```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')
```

### Step 3.2: Create Authentication Routes

**Create app/routes/__init__.py:**
```python
# Empty file to make routes a package
```

**Create app/routes/auth.py:**
```python
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.is_admin else 'employee.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('admin.dashboard' if user.is_admin else 'employee.dashboard')
            return redirect(next_page)
        flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
```

### Step 3.3: Create Base Templates

**Create app/templates/layouts/base.html:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Manufacturing Workload Manager{% endblock %}</title>
    {{ bootstrap.load_css() }}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'includes/navbar.html' %}
    
    <main class="container mt-4">
        {% include 'includes/flash_messages.html' %}
        {% block content %}{% endblock %}
    </main>
    
    {{ bootstrap.load_js() }}
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

## Phase 4: Core Feature Implementation

### Step 4.1: Admin Dashboard

**Create app/routes/admin.py:**
```python
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Project, Assignment
from datetime import datetime, date

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get dashboard statistics
    total_projects = Project.query.count()
    unassigned_projects = Project.query.filter_by(status='unassigned').count()
    at_risk_projects = Project.query.filter(
        Project.deadline < date.today(),
        Project.status != 'completed'
    ).count()
    
    # Get team workload
    team_workload = db.session.query(
        User.team_id,
        db.func.count(Assignment.id).label('active_assignments'),
        db.func.sum(Assignment.hours_remaining).label('total_hours')
    ).join(Assignment).filter(
        Assignment.status.in_(['not_started', 'in_progress'])
    ).group_by(User.team_id).all()
    
    return render_template('admin/dashboard.html',
                         total_projects=total_projects,
                         unassigned_projects=unassigned_projects,
                         at_risk_projects=at_risk_projects,
                         team_workload=team_workload)

@bp.route('/assign-project/<int:project_id>')
@login_required
@admin_required
def assign_project(project_id):
    # Assignment logic here
    pass
```

### Step 4.2: Employee Dashboard

**Create app/routes/employee.py:**
```python
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Assignment, Project
from datetime import datetime

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get employee's current assignments
    assignments = Assignment.query.filter_by(
        user_id=current_user.id
    ).join(Project).filter(
        Assignment.status.in_(['not_started', 'in_progress', 'on_hold'])
    ).all()
    
    return render_template('employee/dashboard.html', assignments=assignments)

@bp.route('/update-status/<int:assignment_id>', methods=['POST'])
@login_required
def update_status(assignment_id):
    # Status update logic here
    pass
```

### Step 4.3: Project Import Feature

**Create app/routes/api.py:**
```python
from flask import Blueprint, jsonify, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Project
from datetime import datetime, timedelta
import pandas as pd

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/import-projects', methods=['POST'])
@login_required
def import_projects():
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Import logic here
    pass

@bp.route('/sync-database', methods=['POST'])
@login_required
def sync_database():
    # Database sync logic here
    pass
```

## Phase 5: Testing and Deployment

### Step 5.1: Create Unit Tests

**Create tests/test_models.py:**
```python
import unittest
from app import create_app, db
from app.models import User, Project

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_password_hashing(self):
        u = User(username='test', email='test@example.com')
        u.set_password('password')
        self.assertFalse(u.check_password('wrongpassword'))
        self.assertTrue(u.check_password('password'))
```

### Step 5.2: Prepare for Railway Deployment

**Create nixpacks.toml:**
```toml
[start]
cmd = "gunicorn run:app"
```

**Create Procfile:**
```
web: gunicorn run:app
```

### Step 5.3: Deploy to Railway

1. Push code to GitHub repository
2. Connect GitHub repo to Railway
3. Railway will auto-detect Flask app
4. Add PostgreSQL database service
5. Set environment variables in Railway dashboard:
   - `SECRET_KEY`: Generate secure key
   - `FLASK_ENV`: Set to "production"

### Step 5.4: Run Database Migrations on Railway
```bash
railway run flask db upgrade
```

## Phase 6: Final Features and Polish

### Step 6.1: Implement Hour Tracking
- Add real-time hour calculation
- Create hour display components
- Implement AJAX updates

### Step 6.2: Add Skills Import
- Create file upload interface
- Parse Excel/CSV files
- Validate and import skills data

### Step 6.3: Generate Reports
- Create report templates
- Implement export functionality
- Add download endpoints

### Step 6.4: UI/UX Improvements
- Add loading indicators
- Implement error handling
- Create responsive layouts
- Add confirmation dialogs

## Development Checklist

- [ ] Project setup and configuration
- [ ] Database models created
- [ ] Authentication system working
- [ ] Admin dashboard functional
- [ ] Employee dashboard functional
- [ ] Project assignment logic implemented
- [ ] Hour tracking system working
- [ ] Skills matrix import functional
- [ ] Database sync operational
- [ ] Reports generation working
- [ ] Unit tests written
- [ ] Deployed to Railway
- [ ] Production database migrated
- [ ] SSL/HTTPS configured
- [ ] Performance optimization complete

## Next Steps for AI Assistant

1. Start with Phase 1: Create the project structure and initial configuration
2. Test each component before moving to the next phase
3. Commit changes regularly to version control
4. Document any deviations or improvements
5. Test thoroughly in local development before deploying
6. Deploy to Railway and verify production functionality

This development guide provides a clear roadmap for building the manufacturing webapp step by step. 