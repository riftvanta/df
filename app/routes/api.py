from flask import Blueprint, jsonify, request, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Project, Assignment, User, SkillsMatrix, Vacation
from datetime import datetime, timedelta, date
import pandas as pd
import json
from werkzeug.utils import secure_filename
import os

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/import-projects', methods=['POST'])
@login_required
def import_projects():
    """Import projects from uploaded CSV/Excel file"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read the file based on extension
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = [
                'project_number', 'model_type', 'customer_country', 
                'estimated_hours', 'assembly_start_date', 'deadline'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return jsonify({
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }), 400
            
            # Process each row
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Check if project already exists
                    existing_project = Project.query.filter_by(
                        project_number=row['project_number']
                    ).first()
                    
                    if existing_project:
                        skipped_count += 1
                        continue
                    
                    # Calculate if REF is required first
                    requires_ref_first = (
                        (row['model_type'] == 'PPH' and row['customer_country'] == 'USA') or
                        row['model_type'] in ['APS', 'PSC']
                    )
                    
                    # Create new project
                    project = Project(
                        project_number=row['project_number'],
                        model_type=row['model_type'],
                        customer_country=row['customer_country'],
                        difficulty_level=row.get('difficulty_level', 3),
                        estimated_hours=float(row['estimated_hours']),
                        assembly_start_date=pd.to_datetime(row['assembly_start_date']).date(),
                        deadline=pd.to_datetime(row['deadline']).date(),
                        requires_ref_first=requires_ref_first,
                        status='unassigned'
                    )
                    
                    db.session.add(project)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f'Row {index + 1}: {str(e)}')
                    continue
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'imported': imported_count,
                'skipped': skipped_count,
                'errors': errors
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'File processing error: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@bp.route('/sync-database', methods=['POST'])
@login_required
def sync_database():
    """Sync with external database (mock implementation)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Mock database sync - in real implementation, this would connect to company database
        # For now, we'll just update project statuses based on assignments
        
        updated_projects = 0
        
        # Update project statuses based on assignments
        projects_with_assignments = db.session.query(Project).join(Assignment).all()
        
        for project in projects_with_assignments:
            assignment = Assignment.query.filter_by(project_id=project.id).first()
            if assignment:
                if assignment.status == 'completed' and project.status != 'completed':
                    project.status = 'completed'
                    updated_projects += 1
                elif assignment.status in ['in_progress', 'on_hold'] and project.status != 'in_progress':
                    project.status = 'in_progress'
                    updated_projects += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_projects': updated_projects,
            'last_sync': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sync error: {str(e)}'}), 500

@bp.route('/import-skills', methods=['POST'])
@login_required
def import_skills():
    """Import skills matrix from uploaded CSV/Excel file"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read the file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = ['username', 'machine_type', 'skill_level', 'efficiency_factor']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return jsonify({
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }), 400
            
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Find user by username
                    user = User.query.filter_by(username=row['username']).first()
                    if not user:
                        errors.append(f'Row {index + 1}: User {row["username"]} not found')
                        continue
                    
                    # Check if skill already exists
                    existing_skill = SkillsMatrix.query.filter_by(
                        user_id=user.id,
                        machine_type=row['machine_type']
                    ).first()
                    
                    if existing_skill:
                        # Update existing skill
                        existing_skill.skill_level = row['skill_level']
                        existing_skill.efficiency_factor = float(row['efficiency_factor'])
                    else:
                        # Create new skill
                        skill = SkillsMatrix(
                            user_id=user.id,
                            machine_type=row['machine_type'],
                            skill_level=row['skill_level'],
                            efficiency_factor=float(row['efficiency_factor'])
                        )
                        db.session.add(skill)
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f'Row {index + 1}: {str(e)}')
                    continue
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'imported': imported_count,
                'errors': errors
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'File processing error: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@bp.route('/import-vacations', methods=['POST'])
@login_required
def import_vacations():
    """Import vacation schedules from uploaded CSV/Excel file"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read the file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = ['username', 'start_date', 'end_date']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return jsonify({
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }), 400
            
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Find user by username
                    user = User.query.filter_by(username=row['username']).first()
                    if not user:
                        errors.append(f'Row {index + 1}: User {row["username"]} not found')
                        continue
                    
                    # Create vacation record
                    vacation = Vacation(
                        user_id=user.id,
                        start_date=pd.to_datetime(row['start_date']).date(),
                        end_date=pd.to_datetime(row['end_date']).date(),
                        approved=row.get('approved', True)
                    )
                    
                    db.session.add(vacation)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f'Row {index + 1}: {str(e)}')
                    continue
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'imported': imported_count,
                'errors': errors
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'File processing error: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@bp.route('/dashboard-stats')
@login_required
def dashboard_stats():
    """Get real-time dashboard statistics"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Calculate statistics
    total_projects = Project.query.count()
    unassigned_projects = Project.query.filter_by(status='unassigned').count()
    at_risk_projects = Project.query.filter(
        Project.deadline < date.today(),
        Project.status != 'completed'
    ).count()
    active_projects = Project.query.filter(
        Project.status.in_(['assigned', 'in_progress'])
    ).count()
    
    return jsonify({
        'total_projects': total_projects,
        'unassigned_projects': unassigned_projects,
        'at_risk_projects': at_risk_projects,
        'active_projects': active_projects,
        'last_updated': datetime.utcnow().isoformat()
    })

@bp.route('/auto-assign-project/<int:project_id>', methods=['POST'])
@login_required
def auto_assign_project(project_id):
    """Automatically assign project to best available employee"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    project = Project.query.get_or_404(project_id)
    
    # Check if already assigned
    if Assignment.query.filter_by(project_id=project_id).first():
        return jsonify({'error': 'Project already assigned'}), 400
    
    # Find best employee using the same logic as admin routes
    from app.routes.admin import get_suitable_employees
    suitable_employees = get_suitable_employees(project)
    
    if not suitable_employees:
        return jsonify({'error': 'No suitable employees available'}), 400
    
    # Assign to best employee (first in sorted list)
    best_employee = suitable_employees[0]
    employee = best_employee['employee']
    
    # Create assignment
    assignment = Assignment(
        project_id=project_id,
        user_id=employee.id,
        status='not_started',
        hours_remaining=project.estimated_hours,
        assigned_at=datetime.utcnow()
    )
    
    project.status = 'assigned'
    
    db.session.add(assignment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'assigned_to': employee.username,
        'skill_level': best_employee['skill_level'],
        'available_hours': best_employee['available_hours']
    })

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 