from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Assignment, Project, User
from datetime import datetime

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Employee dashboard showing current assignments and work status"""
    # Get employee's current assignments
    assignments = db.session.query(Assignment, Project).join(
        Project, Assignment.project_id == Project.id
    ).filter(
        Assignment.user_id == current_user.id,
        Assignment.status.in_(['not_started', 'in_progress', 'on_hold'])
    ).order_by(Project.deadline.asc()).all()
    
    # Get completed assignments (last 5)
    completed_assignments = db.session.query(Assignment, Project).join(
        Project, Assignment.project_id == Project.id
    ).filter(
        Assignment.user_id == current_user.id,
        Assignment.status == 'completed'
    ).order_by(Assignment.completed_at.desc()).limit(5).all()
    
    # Calculate total remaining hours
    total_remaining_hours = sum(
        assignment.hours_remaining or 0 
        for assignment, project in assignments
    )
    
    # Get workload summary
    workload_summary = {
        'total_assignments': len(assignments),
        'total_hours': total_remaining_hours,
        'not_started': len([a for a, p in assignments if a.status == 'not_started']),
        'in_progress': len([a for a, p in assignments if a.status == 'in_progress']),
        'on_hold': len([a for a, p in assignments if a.status == 'on_hold']),
        'completed_this_week': len(completed_assignments)
    }
    
    return render_template('employee/dashboard.html',
                         assignments=assignments,
                         completed_assignments=completed_assignments,
                         workload_summary=workload_summary)

@bp.route('/update-status/<int:assignment_id>', methods=['POST'])
@login_required
def update_status(assignment_id):
    """Update assignment status with optional hold reason"""
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Verify this assignment belongs to the current user
    if assignment.user_id != current_user.id:
        flash('You can only update your own assignments.', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    new_status = request.form.get('status')
    hold_reason = request.form.get('hold_reason', '')
    hours_remaining = request.form.get('hours_remaining', type=float)
    
    if new_status not in ['not_started', 'in_progress', 'on_hold', 'completed']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    # Update assignment
    old_status = assignment.status
    assignment.status = new_status
    assignment.last_status_change = datetime.utcnow()
    
    # Handle specific status changes
    if new_status == 'in_progress' and old_status != 'in_progress':
        assignment.started_at = datetime.utcnow()
        flash('Work started on project.', 'success')
        
    elif new_status == 'completed':
        assignment.completed_at = datetime.utcnow()
        assignment.hours_remaining = 0
        # Update project status if this was the only assignment
        project = Project.query.get(assignment.project_id)
        project.status = 'completed'
        flash('Project marked as completed!', 'success')
        
    elif new_status == 'on_hold':
        assignment.hold_reason = hold_reason
        flash(f'Work put on hold: {hold_reason}', 'info')
        
    elif new_status == 'in_progress' and old_status == 'on_hold':
        assignment.hold_reason = None
        flash('Work resumed.', 'success')
    
    # Update hours remaining if provided
    if hours_remaining is not None and hours_remaining >= 0:
        assignment.hours_remaining = hours_remaining
    
    db.session.commit()
    
    return redirect(url_for('employee.dashboard'))

@bp.route('/assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    """View detailed information about a specific assignment"""
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Verify this assignment belongs to the current user
    if assignment.user_id != current_user.id:
        flash('You can only view your own assignments.', 'danger')
        return redirect(url_for('employee.dashboard'))
    
    project = Project.query.get(assignment.project_id)
    
    # Calculate time spent vs remaining
    time_spent = (project.estimated_hours or 0) - (assignment.hours_remaining or 0)
    
    return render_template('employee/assignment_detail.html',
                         assignment=assignment,
                         project=project,
                         time_spent=time_spent)

@bp.route('/update-hours/<int:assignment_id>', methods=['POST'])
@login_required
def update_hours(assignment_id):
    """Update remaining hours for an assignment"""
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Verify this assignment belongs to the current user
    if assignment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    hours_remaining = request.form.get('hours_remaining', type=float)
    
    if hours_remaining is None or hours_remaining < 0:
        return jsonify({'error': 'Invalid hours value'}), 400
    
    assignment.hours_remaining = hours_remaining
    assignment.last_status_change = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'hours_remaining': hours_remaining,
        'message': 'Hours updated successfully'
    })

@bp.route('/hold-reasons')
@login_required
def get_hold_reasons():
    """Get list of available hold reasons"""
    hold_reasons = [
        'Waiting for REF team feedback',
        'Waiting for electrical team feedback',
        'Moving to work on urgent project',
        'Waiting for parts/materials',
        'Technical issue needs resolution',
        'Waiting for customer clarification',
        'Other'
    ]
    return jsonify(hold_reasons)

@bp.route('/workload-summary')
@login_required
def workload_summary():
    """Get current workload summary for AJAX updates"""
    # Get current assignments
    assignments = Assignment.query.filter_by(
        user_id=current_user.id
    ).filter(
        Assignment.status.in_(['not_started', 'in_progress', 'on_hold'])
    ).all()
    
    total_hours = sum(a.hours_remaining or 0 for a in assignments)
    
    summary = {
        'total_assignments': len(assignments),
        'total_hours': total_hours,
        'not_started': len([a for a in assignments if a.status == 'not_started']),
        'in_progress': len([a for a in assignments if a.status == 'in_progress']),
        'on_hold': len([a for a in assignments if a.status == 'on_hold'])
    }
    
    return jsonify(summary) 