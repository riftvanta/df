# Manufacturing Workload Management App - What to Build

## What This App Does

Build a web application for a manufacturing company to assign work tasks to individual employees. The company has 2 departments with 5 teams total, and about 4 employees per team. Each work project gets assigned to one specific person, not shared between people.

The main problem this solves: Right now they track everything manually, which causes confusion about who's doing what, projects get delayed, and urgent work disrupts planned schedules.

## The Company Setup

The company has two departments:
- **Department 1 (SM Design)**: Has 3 teams that work on different types of machines
  - Team 1: Works on PAH machines for all countries
  - Team 2: Works on PPH machines but only for USA customers  
  - Team 3: Works on PPH machines for non-USA customers
- **Department 2 (REF Design)**: Has 2 teams that work on REF machines
  - Team 4: Works on REF machines for USA customers only
  - Team 5: Works on REF machines for non-USA customers

**Important**: Some employees can help other teams if they have the right skills and are available.

## Critical Business Rule About Dependencies

This is really important: Not all projects need to wait for REF team to finish first. Only these specific types need REF completed first:
- PPH projects going to United States
- APS projects
- PSC projects

All other SM projects can start right away without waiting for REF.

## Who Uses the System

### Admin Users
Admin users can do everything:
- Assign projects to employees
- See all dashboards and reports
- Handle urgent projects
- Add new employees
- Import data from company database
- Export reports

### Employee Users  
Employee users can only:
- Update their own work status
- Put their work on hold (with a reason)
- See their assigned projects
- See how many hours they have left on each project

## What the System Needs to Do

### 1. Assign Work Automatically

The system should automatically suggest which employee should get each project based on:
- **What type of machine** (PAH, PPH, REF)
- **Which country** the customer is in (USA vs everywhere else)
- **How difficult** the project is
- **How many hours** the employee has available
- **What skills** the employee has

When the system can't find anyone available with the right skills, it should:
- Look for employees from other teams who have secondary skills
- If still no one available, mark the project as "At Risk"
- Let the admin manually assign it anyway if needed

### 2. Hour Tracking

Each employee should see how many hours they have left on their current project. The system should:
- Track when they mark work as "In Progress"
- Track when they put work "On Hold"
- Show remaining hours in format like "5.6 hours" or "5 hours, 36 minutes"
- Update when page is refreshed

### 3. Hold Work with Reasons

Employees should be able to pause their work and select why:
- Waiting for REF team feedback
- Waiting for electrical team feedback  
- Moving to work on urgent project

### 4. Connect to Company Database

The system should connect directly to the company's existing database and:
- Import new projects automatically
- Notice when projects are completed and mark them done
- Alert admin when project deadlines change
- Have a "refresh" button to sync latest data

### 5. Skills Matrix

Import a spreadsheet that shows:
- Which employees can work on which machine types
- What their main skills are vs secondary skills
- How long different types of projects usually take

### 6. Admin Dashboard

Show the admin:
- How busy each team is right now
- Which projects are at risk of being late
- Which projects need to be assigned
- Alerts for problems

### 7. Simple Vacation Tracking

Admin can mark when employees are on vacation, and the system won't assign them work during those days.

### 8. Basic Reporting

Generate simple reports showing:
- What was completed yesterday
- Which projects are behind schedule
- How much overtime is being used
- Export current data to spreadsheet

## Technical Requirements

### Database Design

You'll need these main data tables:

**users** - Store employee information
- Basic info like email, password, role (admin or employee)
- Which team they belong to
- How many hours per week they work

**projects** - Store work projects  
- Project details like model type, customer country, difficulty level
- When it needs to be completed
- How many hours it should take
- Current status and who it's assigned to

**assignments** - Track who's working on what
- Which employee is assigned to which project
- Current status (not started, in progress, on hold, completed)
- How many hours are left
- When status last changed

**skills_matrix** - Employee capabilities
- Which employees can work on which machine types
- Main skills vs secondary skills
- Time estimates for different types of work

**vacations** - Track time off
- Which employee is on vacation on which dates

### Technology Stack - Flask Traditional Approach

**Backend Framework**: Flask (Python) - A lightweight WSGI web application framework
**Frontend**: Server-side rendered HTML with Jinja2 templates + Bootstrap for styling
**Database**: PostgreSQL with Flask-SQLAlchemy ORM
**Authentication**: Flask-Login for session management
**Forms**: Flask-WTF for form handling and CSRF protection
**Database Migrations**: Flask-Migrate (Alembic-based)
**Environment Configuration**: python-dotenv for environment variables

### Flask Application Structure

Following Flask best practices, organize the application as a package:

```
manufacturing_app/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── admin.py         # Admin dashboard routes
│   │   ├── employee.py      # Employee dashboard routes
│   │   └── api.py           # API endpoints for AJAX
│   ├── templates/
│   │   ├── base.html        # Base template
│   │   ├── auth/
│   │   ├── admin/
│   │   └── employee/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── forms.py             # WTForms definitions
├── migrations/              # Database migrations
├── config.py               # Configuration classes
├── requirements.txt        # Dependencies
└── run.py                  # Application entry point
```

### Required Flask Extensions

Install these Flask extensions for full functionality:

**Local Development (SQLite)**:
```bash
pip install flask flask-sqlalchemy flask-login flask-wtf flask-migrate
pip install python-dotenv bootstrap-flask pandas gunicorn
```

**Production Dependencies (Additional)**:
```bash
pip install psycopg2-binary  # PostgreSQL adapter for Railway
```

**Complete requirements.txt**:
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

### Flask-Specific Implementation Notes

**Database Models**: Use Flask-SQLAlchemy for ORM with relationship definitions
**Templates**: Leverage Jinja2 template inheritance for consistent UI
**Forms**: Use Flask-WTF for secure form handling with CSRF protection
**Authentication**: Implement Flask-Login for session-based authentication
**Configuration**: Use Flask's config system with environment-specific settings
**Blueprints**: Organize routes using Flask Blueprints for modular structure

### Key Features to Build (Flask Implementation)

1. **Login System**: 
   - Use Flask-Login for session management
   - Create login/logout routes with Flask-WTF forms
   - Implement role-based access control with decorators
   - Store user sessions in Flask's secure session cookies

2. **Assignment Interface**: 
   - Create admin blueprint with assignment routes
   - Use Flask-SQLAlchemy to query available employees and projects
   - Implement AJAX endpoints for real-time project assignment
   - Use Jinja2 templates for dynamic UI updates

3. **Employee Dashboard**: 
   - Build employee blueprint with protected routes
   - Create dashboard template showing current assignments
   - Implement status update forms with Flask-WTF
   - Use Bootstrap components for responsive design

4. **Project Import**: 
   - Create background task routes for database synchronization
   - Use Flask-SQLAlchemy bulk operations for efficient imports
   - Implement CSV/Excel file upload with validation
   - Add progress tracking with Flask sessions

5. **Skills Import**: 
   - Build file upload form with Flask-WTF FileField
   - Parse spreadsheet data with pandas integration
   - Validate and import skills matrix data
   - Provide import status feedback to admin

6. **Hour Tracking**: 
   - Create time calculation functions in models
   - Use SQLAlchemy queries for real-time hour calculations
   - Display remaining hours in Jinja2 templates
   - Implement AJAX refresh for live updates

7. **Hold/Resume**: 
   - Create status update routes with reason selection
   - Use Flask-WTF SelectField for hold reasons
   - Implement modal dialogs with Bootstrap
   - Update database with SQLAlchemy operations

8. **Admin Dashboard**: 
   - Build comprehensive admin blueprint
   - Create dashboard queries for team status
   - Use Chart.js for visual data representation
   - Implement real-time updates with AJAX polling

9. **Basic Reports**: 
   - Create report generation routes
   - Use SQLAlchemy for complex queries
   - Generate CSV/Excel exports with pandas
   - Implement downloadable file responses

### Flask Development Workflow

1. **Setup Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate  # Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   ```bash
   # Create .env file for local development
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-local-secret-key
   DATABASE_URL=sqlite:///manufacturing.db
   ```

4. **Database Setup (Local SQLite)**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run Development Server**:
   ```bash
   flask run
   ```
   
   Your app will be available at `http://localhost:5000` with SQLite database stored locally.

6. **Development Database Management**:
   ```bash
   # View SQLite database
   sqlite3 manufacturing.db
   
   # Reset database (if needed)
   rm manufacturing.db
   flask db upgrade
   
   # Create new migration after model changes
   flask db migrate -m "Description of changes"
   flask db upgrade
   ```

### Flask Configuration Classes

Create environment-specific configurations:
- **DevelopmentConfig**: Debug enabled, SQLite for local development
- **ProductionConfig**: Debug disabled, PostgreSQL with connection pooling for Railway
- **TestingConfig**: In-memory database for unit tests

### Database Configuration

**Local Development (SQLite)**:
```python
# config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'manufacturing.db')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/manufacturing_db'
    
    # Railway-specific optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

**Environment Variables (.env file)**:
```bash
# Local development
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-local-secret-key
DATABASE_URL=sqlite:///manufacturing.db

# Production (Railway will set these)
# DATABASE_URL=postgresql://... (automatically set by Railway)
# SECRET_KEY=your-production-secret-key
```

### Production Deployment on Railway

**Railway** is a modern deployment platform that provides free hosting with automatic PostgreSQL database provisioning. Here's how to deploy your Flask manufacturing app:

#### Railway Setup Requirements

1. **Create Production Files**:

Create `requirements.txt`:
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

Create `nixpacks.toml`:
```toml
# nixpacks.toml
[start]
cmd = "gunicorn run:app"
```

Create `Procfile` (alternative to nixpacks.toml):
```
web: gunicorn run:app
```

#### Railway Deployment Methods

**Option 1: One-Click Deploy (Recommended)**
1. Visit [Railway Flask Template](https://railway.app/new/template/zUcpux)
2. Sign in with GitHub
3. Click "Deploy Now"
4. Railway automatically provisions PostgreSQL database
5. Your app deploys with a `xxx.up.railway.app` domain

**Option 2: Deploy from GitHub Repository**
1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Railway auto-detects Flask app and deploys
4. Add PostgreSQL database service from Railway dashboard

**Option 3: Railway CLI Deployment**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy application
railway up

# Add PostgreSQL database
railway add postgresql

# Generate public domain
railway domain
```

#### Database Migration on Railway

**Automatic Database Setup**:
Railway automatically creates a PostgreSQL database and sets the `DATABASE_URL` environment variable. Your Flask app will automatically use PostgreSQL in production.

**Run Migrations on Railway**:
```bash
# Via Railway CLI
railway run flask db upgrade

# Or set up one-time migration command
railway run python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

#### Environment Configuration for Railway

**Required Environment Variables in Railway Dashboard**:
- `SECRET_KEY`: Strong secret key for production
- `FLASK_ENV`: Set to "production"
- `DATABASE_URL`: Automatically set by Railway PostgreSQL service

#### Railway-Specific Optimizations

**Update `app/__init__.py` for Railway**:
```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config, DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Load configuration based on environment
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.routes import auth, admin, employee, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(employee.bp)
    app.register_blueprint(api.bp)
    
    return app
```

#### Production Readiness Checklist

- [ ] PostgreSQL database connected via Railway
- [ ] Strong SECRET_KEY set in Railway environment
- [ ] Database migrations run successfully
- [ ] Static files served correctly
- [ ] Error handling configured for production
- [ ] Logging configured for Railway monitoring
- [ ] SSL/HTTPS enabled (automatic with Railway)
- [ ] Environment variables properly configured

#### Local Development vs Production

**Local Development**:
- Uses SQLite database file
- Debug mode enabled
- Hot reload active
- Run with `flask run`

**Production (Railway)**:
- Uses PostgreSQL database
- Debug mode disabled
- Gunicorn WSGI server
- Automatic scaling and health checks
- Built-in monitoring and logs

#### Monitoring and Maintenance

**Railway Dashboard Features**:
- Real-time deployment logs
- Database metrics and queries
- Environment variable management
- Custom domain configuration
- Automatic SSL certificates
- Usage analytics and scaling metrics

**Access Railway Services**:
- Application logs: Railway dashboard → Deployments → Logs
- Database access: Railway dashboard → PostgreSQL → Data
- Environment variables: Railway dashboard → Settings → Environment

## Important Rules for Assignment

When assigning projects, follow these rules:
1. Match machine type to employee's primary skills first
2. Consider geography (USA vs non-USA customers)
3. Check if employee has enough available hours
4. If no primary skilled employee available, check secondary skills
5. If still no one available, mark project as "At Risk"
6. Always let admin override automatic assignments

## Critical Calculations

**Project Deadline**: Always calculate as Assembly Start Date minus 14 days
**Available Hours**: Employee's weekly hours minus vacation days minus already assigned work
**Remaining Hours**: Start with estimated hours, count down as work progresses

## What Not to Build (Keep Simple)

Don't build these features initially:
- Complex approval workflows
- Mobile app (web only)
- Automated email notifications
- Advanced analytics or predictions
- Time tracking integration with payroll
- Complex project dependency management

## Success Criteria

The system works if:
- Admin can assign projects quickly without conflicts
- Employees can easily update their work status
- Hour tracking displays accurately
- Projects stop getting "lost" in the system
- Management can see what's happening without asking individuals

## Data Import Requirements

The system needs to import:
- Project data from company database (automatic sync)
- Employee skills from spreadsheet (manual upload)
- Vacation schedules from spreadsheet (manual upload)
- Time estimates for different work types (manual setup)

## Error Handling

Handle these common problems:
- Company database connection fails: Keep working with existing data, show warning
- Employee loses internet during work: Save work status when connection returns
- Two admins try to assign same project: Show error, let second person know it's taken
- Invalid data in imports: Show clear error messages, don't break system

This system should make it easy for the manufacturing company to track and assign work efficiently, while being simple enough that everyone will actually use it. 