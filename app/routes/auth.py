from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db, limiter, cache
from app.models import User
from app.forms import LoginForm, RegistrationForm
from datetime import datetime, timedelta
import hashlib

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """User login with rate limiting and security enhancements"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.is_admin else 'employee.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check for failed login attempts
        failed_attempts_key = f"failed_login_attempts_{request.remote_addr}"
        failed_attempts = cache.get(failed_attempts_key) or 0
        
        if failed_attempts >= 5:
            flash('Too many failed login attempts. Please try again later.', 'danger')
            return render_template('auth/login.html', title='Sign In', form=form)
        
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            # Clear failed attempts on successful login
            cache.delete(failed_attempts_key)
            
            login_user(user, remember=form.remember_me.data)
            
            # Log successful login
            current_app.logger.info(f'User {user.username} logged in successfully from {request.remote_addr}')
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Handle next parameter safely
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin.dashboard' if user.is_admin else 'employee.dashboard')
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page)
        else:
            # Increment failed attempts
            cache.set(failed_attempts_key, failed_attempts + 1, timeout=300)  # 5 minutes
            
            # Log failed login attempt
            current_app.logger.warning(f'Failed login attempt for {form.email.data} from {request.remote_addr}')
            
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Secure logout with session cleanup"""
    username = current_user.username
    
    # Log logout
    current_app.logger.info(f'User {username} logged out')
    
    # Clear session data
    session.clear()
    
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    """User registration with rate limiting"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.is_admin else 'employee.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if registration is allowed (could be admin-only in production)
            if not current_app.config.get('ALLOW_REGISTRATION', True):
                flash('Registration is currently disabled. Please contact an administrator.', 'warning')
                return render_template('auth/register.html', title='Register', form=form)
            
            user = User(
                username=form.username.data.lower(),
                email=form.email.data.lower(),
                role=form.role.data,
                department_id=form.department_id.data,
                team_id=form.team_id.data,
                hours_per_week=form.hours_per_week.data,
                is_active=True
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Log successful registration
            current_app.logger.info(f'New user registered: {user.username} ({user.email})')
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def change_password():
    """Allow users to change their password"""
    from app.forms import ChangePasswordForm
    
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            # Log password change
            current_app.logger.info(f'User {current_user.username} changed password')
            
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('employee.dashboard' if not current_user.is_admin else 'admin.dashboard'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('auth/change_password.html', title='Change Password', form=form)

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', title='Profile', user=current_user)

@bp.route('/update-profile', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def update_profile():
    """Allow users to update their profile"""
    from app.forms import UpdateProfileForm
    
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.email = form.email.data.lower()
        current_user.hours_per_week = form.hours_per_week.data
        
        db.session.commit()
        
        # Log profile update
        current_app.logger.info(f'User {current_user.username} updated profile')
        
        flash('Your profile has been updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
    
    # Pre-populate form with current data
    form.email.data = current_user.email
    form.hours_per_week.data = current_user.hours_per_week
    
    return render_template('auth/update_profile.html', title='Update Profile', form=form)

@bp.route('/')
def index():
    """Root route that redirects to appropriate dashboard or login"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('employee.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

# Security headers for auth routes
@bp.after_request
def after_request(response):
    """Add security headers to auth responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response 