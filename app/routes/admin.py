from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Project, Assignment, SkillsMatrix, Vacation
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func

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
    """Admin dashboard with key statistics and team workload"""
    # Get dashboard statistics
    total_projects = Project.query.count()
    unassigned_projects = Project.query.filter_by(status='unassigned').count()
    
    # Calculate at-risk projects (past deadline and not completed)
    at_risk_projects = Project.query.filter(
        Project.deadline < date.today(),
        Project.status != 'completed'
    ).count()
    
    # Get active projects (in progress)
    active_projects = Project.query.filter(
        Project.status.in_(['assigned', 'in_progress'])
    ).count()
    
    # Get team workload summary
    team_workload = db.session.query(
        User.team_id,
        func.count(Assignment.id).label('active_assignments'),
        func.sum(Assignment.hours_remaining).label('total_hours'),
        func.count(User.id).label('team_size')
    ).outerjoin(Assignment, and_(
        Assignment.user_id == User.id,
        Assignment.status.in_(['not_started', 'in_progress'])
    )).group_by(User.team_id).all()
    
    # Get recent activity (last 10 assignments)
    recent_assignments = db.session.query(Assignment, Project, User).join(
        Project, Assignment.project_id == Project.id
    ).join(
        User, Assignment.user_id == User.id
    ).order_by(Assignment.last_status_change.desc()).limit(10).all()
    
    # Get projects needing assignment
    unassigned_projects_list = Project.query.filter_by(status='unassigned').limit(5).all()
    
    # Get projects at risk
    at_risk_projects_list = Project.query.filter(
        Project.deadline < date.today(),
        Project.status != 'completed'
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_projects=total_projects,
                         unassigned_projects=unassigned_projects,
                         at_risk_projects=at_risk_projects,
                         active_projects=active_projects,
                         team_workload=team_workload,
                         recent_assignments=recent_assignments,
                         unassigned_projects_list=unassigned_projects_list,
                         at_risk_projects_list=at_risk_projects_list)

@bp.route('/projects')
@login_required
@admin_required
def projects():
    """View all projects with filtering and sorting options"""
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'deadline')
    
    # Base query
    query = Project.query
    
    # Apply status filter
    if status_filter != 'all':
        query = query.filter(Project.status == status_filter)
    
    # Apply sorting
    if sort_by == 'deadline':
        query = query.order_by(Project.deadline.asc())
    elif sort_by == 'created':
        query = query.order_by(Project.created_at.desc())
    elif sort_by == 'project_number':
        query = query.order_by(Project.project_number.asc())
    
    projects = query.all()
    
    # Get assignment info for each project
    project_assignments = {}
    for project in projects:
        assignment = Assignment.query.filter_by(project_id=project.id).first()
        if assignment:
            project_assignments[project.id] = {
                'employee': User.query.get(assignment.user_id),
                'status': assignment.status,
                'hours_remaining': assignment.hours_remaining
            }
    
    return render_template('admin/projects.html',
                         projects=projects,
                         project_assignments=project_assignments,
                         status_filter=status_filter,
                         sort_by=sort_by)

@bp.route('/assign-project/<int:project_id>')
@login_required
@admin_required
def assign_project(project_id):
    """Show project assignment interface"""
    project = Project.query.get_or_404(project_id)
    
    # Get suitable employees based on skills
    suitable_employees = get_suitable_employees(project)
    
    return render_template('admin/assign_project.html',
                         project=project,
                         suitable_employees=suitable_employees)

@bp.route('/assign-project', methods=['POST'])
@login_required
@admin_required
def assign_project_submit():
    """Process project assignment"""
    project_id = request.form.get('project_id', type=int)
    employee_id = request.form.get('employee_id', type=int)
    
    project = Project.query.get_or_404(project_id)
    employee = User.query.get_or_404(employee_id)
    
    # Check if project is already assigned
    existing_assignment = Assignment.query.filter_by(project_id=project_id).first()
    if existing_assignment:
        flash('This project is already assigned to someone else.', 'danger')
        return redirect(url_for('admin.projects'))
    
    # Create assignment
    assignment = Assignment(
        project_id=project_id,
        user_id=employee_id,
        status='not_started',
        hours_remaining=project.estimated_hours,
        assigned_at=datetime.utcnow()
    )
    
    # Update project status
    project.status = 'assigned'
    
    db.session.add(assignment)
    db.session.commit()
    
    flash(f'Project {project.project_number} assigned to {employee.username}', 'success')
    return redirect(url_for('admin.projects'))

@bp.route('/employees')
@login_required
@admin_required
def employees():
    """View all employees with their current workload"""
    employees = User.query.filter_by(role='employee').all()
    
    # Get workload for each employee
    employee_workload = {}
    for employee in employees:
        active_assignments = Assignment.query.filter_by(
            user_id=employee.id
        ).filter(
            Assignment.status.in_(['not_started', 'in_progress'])
        ).all()
        
        total_hours = sum(a.hours_remaining or 0 for a in active_assignments)
        employee_workload[employee.id] = {
            'active_assignments': len(active_assignments),
            'total_hours': total_hours,
            'assignments': active_assignments
        }
    
    return render_template('admin/employees.html',
                         employees=employees,
                         employee_workload=employee_workload)

@bp.route('/reports')
@login_required
@admin_required
def reports():
    """Generate basic reports"""
    # Daily completion report
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    completed_yesterday = Assignment.query.filter(
        Assignment.status == 'completed',
        Assignment.completed_at >= yesterday,
        Assignment.completed_at < today
    ).count()
    
    # Projects behind schedule
    behind_schedule = Project.query.filter(
        Project.deadline < today,
        Project.status != 'completed'
    ).count()
    
    # Team productivity (assignments completed this week)
    week_start = today - timedelta(days=today.weekday())
    weekly_completions = db.session.query(
        User.team_id,
        func.count(Assignment.id).label('completions')
    ).join(Assignment).filter(
        Assignment.status == 'completed',
        Assignment.completed_at >= week_start
    ).group_by(User.team_id).all()
    
    return render_template('admin/reports.html',
                         completed_yesterday=completed_yesterday,
                         behind_schedule=behind_schedule,
                         weekly_completions=weekly_completions)

def get_suitable_employees(project):
    """Find employees suitable for a project based on skills and availability"""
    # Get employees with matching skills
    suitable_skills = SkillsMatrix.query.filter_by(
        machine_type=project.model_type
    ).all()
    
    suitable_employees = []
    
    for skill in suitable_skills:
        employee = User.query.get(skill.user_id)
        if not employee or employee.role != 'employee':
            continue
            
        # Check if employee is on vacation
        is_on_vacation = Vacation.query.filter(
            Vacation.user_id == employee.id,
            Vacation.start_date <= date.today(),
            Vacation.end_date >= date.today(),
            Vacation.approved == True
        ).first() is not None
        
        if is_on_vacation:
            continue
            
        # Calculate current workload
        current_hours = db.session.query(
            func.sum(Assignment.hours_remaining)
        ).filter_by(
            user_id=employee.id
        ).filter(
            Assignment.status.in_(['not_started', 'in_progress'])
        ).scalar() or 0
        
        # Check team geography constraints
        can_work_on_project = check_team_geography_constraints(employee, project)
        
        if can_work_on_project:
            suitable_employees.append({
                'employee': employee,
                'skill_level': skill.skill_level,
                'efficiency_factor': skill.efficiency_factor,
                'current_workload': current_hours,
                'available_hours': max(0, employee.hours_per_week - current_hours),
                'is_on_vacation': is_on_vacation
            })
    
    # Sort by skill level (primary first) and then by availability
    suitable_employees.sort(key=lambda x: (
        x['skill_level'] == 'primary',
        x['available_hours']
    ), reverse=True)
    
    return suitable_employees

def check_team_geography_constraints(employee, project):
    """Check if employee's team can work on this project based on geography constraints"""
    # Team constraints based on the business rules
    team_constraints = {
        1: {'models': ['PAH'], 'countries': 'all'},  # PAH for all countries
        2: {'models': ['PPH'], 'countries': ['USA']},  # PPH for USA only
        3: {'models': ['PPH'], 'countries': 'non_USA'},  # PPH for non-USA
        4: {'models': ['REF'], 'countries': ['USA']},  # REF for USA only
        5: {'models': ['REF'], 'countries': 'non_USA'},  # REF for non-USA
    }
    
    team_id = employee.team_id
    if team_id not in team_constraints:
        return False
        
    constraint = team_constraints[team_id]
    
    # Check model type
    if project.model_type not in constraint['models']:
        return False
        
    # Check geography
    if constraint['countries'] == 'all':
        return True
    elif constraint['countries'] == 'non_USA':
        return project.customer_country != 'USA'
    elif isinstance(constraint['countries'], list):
        return project.customer_country in constraint['countries']
    
    return False 