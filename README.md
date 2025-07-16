# Manufacturing Workload Management App

A comprehensive web application for managing manufacturing project assignments, employee workloads, and team productivity built with Flask and PostgreSQL.

## 🚀 Features

### Admin Dashboard
- **Real-time Statistics**: Total projects, unassigned projects, at-risk projects, and active projects
- **Team Workload Visualization**: Visual progress bars showing team capacity and current workload
- **Smart Project Assignment**: Automatic employee matching based on skills, geography, and availability
- **Data Import**: CSV/Excel import for projects, skills, and vacation schedules
- **Database Sync**: Manual database synchronization with external systems
- **Recent Activity Tracking**: Real-time view of assignment status changes

### Employee Dashboard
- **Personal Workload**: Overview with hours remaining and project counts
- **Assignment Management**: Visual cards for each project with status indicators
- **Real-time Hour Tracking**: AJAX-powered hour updates
- **Status Management**: Easy status updates (Start Work, Put on Hold, Resume, Complete)
- **Hold Reasons**: Predefined hold reasons for project delays
- **Progress Tracking**: Visual progress bars and time spent calculations

### Smart Assignment Logic
- **Skills-based Matching**: Matches projects to employees based on machine type skills
- **Geography Constraints**: Implements business rules for team-country assignments
- **Availability Checking**: Considers current workload and vacation schedules
- **Efficiency Factors**: Takes into account employee skill levels and efficiency ratings

## 🛠 Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (Railway) / SQLite (Local Development)
- **Frontend**: Server-side rendered HTML with Jinja2 templates
- **UI Framework**: Bootstrap 5 with custom CSS
- **Authentication**: Flask-Login with session management
- **Forms**: Flask-WTF with CSRF protection
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Deployment**: Railway with automatic GitHub integration

## 🏗 Business Logic

### Team Structure
- **Department 1 (SM Design)**: 3 teams working on different machine types
  - Team 1: PAH machines for all countries
  - Team 2: PPH machines for USA customers only
  - Team 3: PPH machines for non-USA customers
- **Department 2 (REF Design)**: 2 teams working on REF machines
  - Team 4: REF machines for USA customers only
  - Team 5: REF machines for non-USA customers

### Critical Business Rules
- **REF Dependency**: Only specific project types need REF completion first:
  - PPH projects going to United States
  - APS projects
  - PSC projects
- **Skills Matrix**: Primary vs secondary skills with efficiency factors
- **Geography Constraints**: Team-country assignment rules
- **Workload Management**: 40-hour work weeks with overflow handling

## 🚀 Railway Deployment

### Prerequisites
- GitHub account
- Railway account (free tier available)
- Fork or clone this repository

### Automatic Deployment Setup

1. **Connect to Railway**:
   - Go to [Railway](https://railway.app)
   - Sign in with your GitHub account
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository

2. **Add PostgreSQL Database**:
   - In your Railway project dashboard
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically set `DATABASE_URL` environment variable

3. **Configure Environment Variables**:
   - Go to your service settings
   - Add the following variables:
     ```
     SECRET_KEY=your-strong-secret-key-here
     FLASK_ENV=production
     ```

4. **Initialize Database**:
   - Railway will automatically deploy your app
   - Run the initialization script: `python railway_init.py`
   - Or trigger it through Railway's interface

### Manual Database Initialization

If you need to manually initialize the database:

```bash
# In Railway's project terminal or locally with production DATABASE_URL
python railway_init.py
```

### Deployment Features

- **Automatic Deployment**: Every push to main branch triggers deployment
- **PostgreSQL Integration**: Automatic database connection
- **Health Checks**: Built-in health endpoint at `/health`
- **Production Optimizations**: Connection pooling, error handling
- **SSL/HTTPS**: Automatically enabled by Railway

## 💻 Local Development

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/riftvanta/df.git
   cd df
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Create .env file
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=dev-secret-key
   DATABASE_URL=sqlite:///manufacturing.db
   ```

5. **Initialize database**:
   ```bash
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   python seed_data.py
   ```

6. **Run the application**:
   ```bash
   flask run
   ```

Visit `http://localhost:5000` to access the application.

## 📊 Default Login Credentials

### Production (Railway)
- **Admin**: `admin@manufacturing.com` / `admin123`
- **Employee**: Any employee account with password `employee123`

### Sample Employee Accounts
- `john_pah@manufacturing.com` (PAH Team)
- `bob_pph_usa@manufacturing.com` (PPH USA Team)
- `charlie_pph_intl@manufacturing.com` (PPH International Team)
- `eve_ref_usa@manufacturing.com` (REF USA Team)
- `grace_ref_intl@manufacturing.com` (REF International Team)

## 📁 Project Structure

```
manufacturing_app/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models.py                # Database models
│   ├── routes/
│   │   ├── auth.py              # Authentication routes
│   │   ├── admin.py             # Admin dashboard routes
│   │   ├── employee.py          # Employee dashboard routes
│   │   └── api.py               # API endpoints
│   ├── templates/
│   │   ├── layouts/base.html    # Base template
│   │   ├── auth/                # Authentication templates
│   │   ├── admin/               # Admin dashboard templates
│   │   └── employee/            # Employee dashboard templates
│   ├── static/
│   │   ├── css/                 # Custom styles
│   │   └── js/                  # Custom JavaScript
│   └── forms.py                 # WTForms definitions
├── config.py                    # Configuration classes
├── requirements.txt             # Dependencies
├── run.py                       # Application entry point
├── railway_init.py              # Railway database initialization
├── seed_data.py                 # Local development seed data
└── nixpacks.toml               # Railway deployment configuration
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/register` - User registration (admin only)

### Admin Dashboard
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/projects` - Project management
- `GET /admin/employees` - Employee management
- `POST /admin/assign-project` - Project assignment
- `GET /admin/reports` - Generate reports

### Employee Dashboard
- `GET /employee/dashboard` - Employee dashboard
- `POST /employee/update-status/<id>` - Update assignment status
- `POST /employee/update-hours/<id>` - Update remaining hours
- `GET /employee/assignment/<id>` - Assignment details

### API Endpoints
- `POST /api/import-projects` - Import projects from CSV/Excel
- `POST /api/import-skills` - Import skills matrix
- `POST /api/import-vacations` - Import vacation schedules
- `POST /api/sync-database` - Sync with external database
- `POST /api/auto-assign-project/<id>` - Auto-assign project
- `GET /api/dashboard-stats` - Real-time dashboard statistics

## 📈 Monitoring & Maintenance

### Health Checks
- **Health Endpoint**: `/health` - Application health status
- **Database Status**: Automatic connection health checks
- **Railway Monitoring**: Built-in service monitoring

### Logging
- Application logs available in Railway dashboard
- Database query logging in development mode
- Error tracking with detailed stack traces

### Backup & Recovery
- Railway automatic PostgreSQL backups
- Database migration support with Flask-Migrate
- Data export capabilities through admin interface

## 🔐 Security Features

- **CSRF Protection**: Flask-WTF CSRF tokens
- **Session Management**: Secure session handling
- **Password Hashing**: Werkzeug password hashing
- **Role-based Access**: Admin vs Employee permissions
- **Input Validation**: WTForms validation
- **SQL Injection Protection**: SQLAlchemy ORM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- Check the [Issues](https://github.com/riftvanta/df/issues) page
- Create a new issue with detailed description
- Include error logs and steps to reproduce

## 🎯 Future Enhancements

- [ ] Email notifications for assignment changes
- [ ] Advanced analytics and reporting
- [ ] Mobile app integration
- [ ] Integration with external manufacturing systems
- [ ] Real-time collaboration features
- [ ] Advanced project dependency management

---

**Manufacturing Workload Management App** - Built with ❤️ using Flask and Railway 