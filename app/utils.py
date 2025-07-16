"""
Utility functions for the Manufacturing Workload Management App
"""

from datetime import datetime, date, timedelta
from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from app import db, cache
from app.models import User, Project, Assignment, SkillsMatrix, Vacation
from sqlalchemy import and_, or_, func
import re

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_project_deadline(assembly_start_date, buffer_days=14):
    """Calculate project deadline based on assembly start date"""
    if isinstance(assembly_start_date, str):
        assembly_start_date = datetime.strptime(assembly_start_date, '%Y-%m-%d').date()
    return assembly_start_date - timedelta(days=buffer_days)

def determine_ref_dependency(model_type, customer_country):
    """Determine if a project requires REF team completion first"""
    ref_required_conditions = [
        (model_type == 'PPH' and customer_country.upper() == 'USA'),
        (model_type == 'APS'),
        (model_type == 'PSC')
    ]
    return any(ref_required_conditions)

def get_team_for_project(model_type, customer_country):
    """Get appropriate team ID for a project based on model type and country"""
    model_type = model_type.upper()
    country = customer_country.upper()
    
    team_mapping = {
        'PAH': 1,  # Team 1 - All countries
        'PPH': 2 if country == 'USA' else 3,  # Team 2 (USA) or Team 3 (Non-USA)
        'REF': 4 if country == 'USA' else 5,  # Team 4 (USA) or Team 5 (Non-USA)
        'APS': 1,  # Default to Team 1
        'PSC': 1   # Default to Team 1
    }
    
    return team_mapping.get(model_type, 1)

def find_best_employee_for_assignment(project):
    """Find the best employee for a project assignment based on skills and availability"""
    
    # Get required team for the project
    required_team = get_team_for_project(project.model_type, project.customer_country)
    
    # Query employees with required skills
    primary_skilled_employees = db.session.query(User).join(SkillsMatrix).filter(
        and_(
            User.is_active == True,
            User.role == 'employee',
            SkillsMatrix.machine_type == project.model_type,
            SkillsMatrix.skill_level == 'primary',
            User.team_id == required_team
        )
    ).all()
    
    # If no primary skilled employees, look for secondary skilled
    if not primary_skilled_employees:
        secondary_skilled_employees = db.session.query(User).join(SkillsMatrix).filter(
            and_(
                User.is_active == True,
                User.role == 'employee',
                SkillsMatrix.machine_type == project.model_type,
                SkillsMatrix.skill_level == 'secondary'
            )
        ).all()
        
        if secondary_skilled_employees:
            primary_skilled_employees = secondary_skilled_employees
    
    if not primary_skilled_employees:
        return None
    
    # Find employee with most available hours
    best_employee = None
    max_available_hours = 0
    
    for employee in primary_skilled_employees:
        available_hours = employee.get_available_hours()
        if available_hours > max_available_hours:
            max_available_hours = available_hours
            best_employee = employee
    
    return best_employee if max_available_hours >= project.estimated_hours else None

def get_dashboard_statistics():
    """Get dashboard statistics for admin"""
    stats = {
        'total_projects': Project.query.count(),
        'unassigned_projects': Project.query.filter_by(status='unassigned').count(),
        'active_projects': Project.query.filter(
            Project.status.in_(['assigned', 'in_progress'])
        ).count(),
        'completed_projects': Project.query.filter_by(status='completed').count(),
        'overdue_projects': Project.query.filter(
            and_(
                Project.deadline < date.today(),
                Project.status.notin_(['completed', 'cancelled'])
            )
        ).count(),
        'urgent_projects': Project.query.filter_by(priority='urgent').count()
    }
    return stats

def get_team_workload_summary():
    """Get team workload summary"""
    team_workload = db.session.query(
        User.team_id,
        func.count(User.id).label('team_size'),
        func.count(Assignment.id).label('active_assignments'),
        func.sum(Assignment.hours_remaining).label('total_hours')
    ).outerjoin(Assignment, and_(
        Assignment.user_id == User.id,
        Assignment.status.in_(['not_started', 'in_progress'])
    )).filter(
        User.is_active == True,
        User.role == 'employee'
    ).group_by(User.team_id).all()
    
    return team_workload

def get_project_priority_score(project):
    """Calculate priority score for project assignment"""
    score = 0
    
    # Base score by priority
    priority_scores = {
        'urgent': 100,
        'high': 75,
        'normal': 50,
        'low': 25
    }
    score += priority_scores.get(project.priority, 50)
    
    # Add urgency based on deadline
    days_until_deadline = (project.deadline - date.today()).days
    if days_until_deadline <= 3:
        score += 30
    elif days_until_deadline <= 7:
        score += 20
    elif days_until_deadline <= 14:
        score += 10
    
    # Add difficulty factor
    score += project.difficulty_level * 5
    
    return score

def format_hours_display(hours):
    """Format hours for display (e.g., 5.5 hours, 1 hour, etc.)"""
    if hours is None:
        return "0 hours"
    
    if hours == 0:
        return "0 hours"
    elif hours == 1:
        return "1 hour"
    elif hours == int(hours):
        return f"{int(hours)} hours"
    else:
        return f"{hours:.1f} hours"

def get_employee_workload(user_id):
    """Get detailed workload information for an employee"""
    assignments = Assignment.query.filter(
        and_(
            Assignment.user_id == user_id,
            Assignment.status.in_(['not_started', 'in_progress', 'on_hold'])
        )
    ).all()
    
    total_hours = sum(assignment.hours_remaining for assignment in assignments)
    
    workload = {
        'total_assignments': len(assignments),
        'total_hours': total_hours,
        'assignments_by_status': {
            'not_started': len([a for a in assignments if a.status == 'not_started']),
            'in_progress': len([a for a in assignments if a.status == 'in_progress']),
            'on_hold': len([a for a in assignments if a.status == 'on_hold'])
        },
        'assignments': assignments
    }
    
    return workload

def validate_project_assignment(project_id, user_id):
    """Validate if a project can be assigned to a user"""
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    
    # Check if project is already assigned
    if project.status not in ['unassigned']:
        return False, "Project is already assigned"
    
    # Check if user is active
    if not user.is_active:
        return False, "User is not active"
    
    # Check if user has required skills
    required_skill = SkillsMatrix.query.filter(
        and_(
            SkillsMatrix.user_id == user_id,
            SkillsMatrix.machine_type == project.model_type
        )
    ).first()
    
    if not required_skill:
        return False, f"User does not have required skills for {project.model_type}"
    
    # Check if user has available hours
    available_hours = user.get_available_hours()
    if available_hours < project.estimated_hours:
        return False, f"User has only {available_hours} hours available, but project needs {project.estimated_hours}"
    
    return True, "Assignment is valid"

def get_projects_at_risk():
    """Get projects that are at risk of missing deadlines"""
    at_risk_projects = Project.query.filter(
        and_(
            Project.deadline <= date.today() + timedelta(days=7),
            Project.status.notin_(['completed', 'cancelled'])
        )
    ).order_by(Project.deadline.asc()).all()
    
    return at_risk_projects

@cache.memoize(timeout=300)  # Cache for 5 minutes
def get_skills_matrix_summary():
    """Get skills matrix summary (cached)"""
    skills_summary = db.session.query(
        SkillsMatrix.machine_type,
        SkillsMatrix.skill_level,
        func.count(SkillsMatrix.id).label('count'),
        func.avg(SkillsMatrix.efficiency_factor).label('avg_efficiency')
    ).join(User).filter(
        User.is_active == True
    ).group_by(
        SkillsMatrix.machine_type,
        SkillsMatrix.skill_level
    ).all()
    
    return skills_summary

def calculate_project_efficiency(project, assignment):
    """Calculate project efficiency based on employee skills"""
    skill = SkillsMatrix.query.filter(
        and_(
            SkillsMatrix.user_id == assignment.user_id,
            SkillsMatrix.machine_type == project.model_type
        )
    ).first()
    
    if not skill:
        return 1.0
    
    # Base efficiency factor
    efficiency = skill.efficiency_factor
    
    # Adjust based on skill level
    if skill.skill_level == 'primary':
        efficiency *= 1.0
    elif skill.skill_level == 'secondary':
        efficiency *= 0.8
    
    # Adjust based on experience
    if skill.years_experience >= 5:
        efficiency *= 1.1
    elif skill.years_experience >= 2:
        efficiency *= 1.05
    
    return min(efficiency, 2.0)  # Cap at 2.0

def sanitize_filename(filename):
    """Sanitize filename for secure file uploads"""
    # Remove any path separators
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remove special characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1)
        filename = name[:255-len(ext)-1] + '.' + ext
    
    return filename

def log_user_activity(user_id, action, details=None):
    """Log user activity for auditing"""
    current_app.logger.info(f"User {user_id} performed action: {action}")
    if details:
        current_app.logger.info(f"Details: {details}")

def get_vacation_conflicts(user_id, start_date, end_date):
    """Check for vacation conflicts with existing assignments"""
    conflicts = Assignment.query.join(Project).filter(
        and_(
            Assignment.user_id == user_id,
            Assignment.status.in_(['not_started', 'in_progress']),
            Project.deadline >= start_date,
            Project.assembly_start_date <= end_date
        )
    ).all()
    
    return conflicts 