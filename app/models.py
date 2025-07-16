from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index, CheckConstraint, event
from sqlalchemy.orm import validates
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='employee', nullable=False)  # admin or employee
    department_id = db.Column(db.Integer, nullable=False, index=True)
    team_id = db.Column(db.Integer, nullable=False, index=True)
    hours_per_week = db.Column(db.Float, default=40.0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships with proper lazy loading and foreign key specifications
    assignments = db.relationship('Assignment', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    skills = db.relationship('SkillsMatrix', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    
    # Specify foreign keys explicitly to avoid ambiguity
    vacations = db.relationship('Vacation', 
                               foreign_keys='Vacation.user_id',
                               backref='employee', 
                               lazy='dynamic', 
                               cascade='all, delete-orphan')
    
    approved_vacations = db.relationship('Vacation', 
                                        foreign_keys='Vacation.approved_by',
                                        backref='approver', 
                                        lazy='dynamic')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('hours_per_week > 0 AND hours_per_week <= 80', name='valid_hours_per_week'),
        CheckConstraint("role IN ('admin', 'employee')", name='valid_role'),
        CheckConstraint('department_id > 0', name='valid_department_id'),
        CheckConstraint('team_id > 0', name='valid_team_id'),
        Index('idx_user_department_team', 'department_id', 'team_id'),
        Index('idx_user_role_active', 'role', 'is_active'),
        Index('idx_user_last_login', 'last_login'),
    )
    
    @validates('email')
    def validate_email(self, key, address):
        if '@' not in address:
            raise ValueError('Invalid email address')
        return address.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return username.lower()
    
    def set_password(self, password):
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    def get_available_hours(self):
        """Calculate available hours for assignment"""
        # Get currently assigned hours
        assigned_hours = db.session.query(db.func.sum(Assignment.hours_remaining)).filter(
            Assignment.user_id == self.id,
            Assignment.status.in_(['not_started', 'in_progress'])
        ).scalar() or 0
        
        # Consider vacation days
        # Implementation depends on vacation calculation logic
        return max(0, self.hours_per_week - assigned_hours)
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    model_type = db.Column(db.String(20), nullable=False, index=True)  # PAH, PPH, REF, APS, PSC
    customer_country = db.Column(db.String(50), nullable=False, index=True)
    difficulty_level = db.Column(db.Integer, nullable=False)  # 1-5 scale
    estimated_hours = db.Column(db.Float, nullable=False)
    assembly_start_date = db.Column(db.Date, nullable=False, index=True)
    deadline = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default='unassigned', nullable=False, index=True)
    requires_ref_first = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.String(20), default='normal', nullable=False)  # urgent, high, normal, low
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('difficulty_level >= 1 AND difficulty_level <= 5', name='valid_difficulty'),
        CheckConstraint('estimated_hours > 0', name='positive_estimated_hours'),
        CheckConstraint('deadline >= assembly_start_date', name='valid_deadline'),
        CheckConstraint("model_type IN ('PAH', 'PPH', 'REF', 'APS', 'PSC')", name='valid_model_type'),
        CheckConstraint("status IN ('unassigned', 'assigned', 'in_progress', 'on_hold', 'completed', 'cancelled')", name='valid_status'),
        CheckConstraint("priority IN ('urgent', 'high', 'normal', 'low')", name='valid_priority'),
        Index('idx_project_status_deadline', 'status', 'deadline'),
        Index('idx_project_model_country', 'model_type', 'customer_country'),
        Index('idx_project_priority_status', 'priority', 'status'),
    )
    
    @validates('project_number')
    def validate_project_number(self, key, project_number):
        if len(project_number) < 5:
            raise ValueError('Project number must be at least 5 characters long')
        return project_number.upper()
    
    @validates('customer_country')
    def validate_customer_country(self, key, country):
        return country.upper()
    
    @property
    def is_overdue(self):
        return self.deadline < datetime.now().date() and self.status not in ['completed', 'cancelled']
    
    @property
    def days_until_deadline(self):
        return (self.deadline - datetime.now().date()).days
    
    def __repr__(self):
        return f'<Project {self.project_number}>'

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='not_started', nullable=False, index=True)
    hours_remaining = db.Column(db.Float, nullable=False)
    original_hours = db.Column(db.Float, nullable=False)  # Track original estimate
    hold_reason = db.Column(db.String(100))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_status_change = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('hours_remaining >= 0', name='non_negative_hours'),
        CheckConstraint('original_hours > 0', name='positive_original_hours'),
        CheckConstraint("status IN ('not_started', 'in_progress', 'on_hold', 'completed', 'cancelled')", name='valid_assignment_status'),
        Index('idx_assignment_status_user', 'status', 'user_id'),
        Index('idx_assignment_project_status', 'project_id', 'status'),
        db.UniqueConstraint('project_id', 'user_id', name='unique_project_assignment'),
    )
    
    @validates('hours_remaining')
    def validate_hours_remaining(self, key, hours):
        if hours < 0:
            raise ValueError('Hours remaining cannot be negative')
        return hours
    
    @property
    def progress_percentage(self):
        if self.original_hours == 0:
            return 100
        return min(100, ((self.original_hours - self.hours_remaining) / self.original_hours) * 100)
    
    def __repr__(self):
        return f'<Assignment {self.id}: User {self.user_id} -> Project {self.project_id}>'

class SkillsMatrix(db.Model):
    __tablename__ = 'skills_matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    machine_type = db.Column(db.String(20), nullable=False, index=True)  # PAH, PPH, REF
    skill_level = db.Column(db.String(20), nullable=False, index=True)  # primary, secondary
    efficiency_factor = db.Column(db.Float, default=1.0, nullable=False)
    years_experience = db.Column(db.Integer, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('efficiency_factor > 0 AND efficiency_factor <= 2.0', name='valid_efficiency_factor'),
        CheckConstraint('years_experience >= 0', name='non_negative_experience'),
        CheckConstraint("machine_type IN ('PAH', 'PPH', 'REF')", name='valid_machine_type'),
        CheckConstraint("skill_level IN ('primary', 'secondary')", name='valid_skill_level'),
        Index('idx_skills_machine_level', 'machine_type', 'skill_level'),
        Index('idx_skills_user_machine', 'user_id', 'machine_type'),
        db.UniqueConstraint('user_id', 'machine_type', name='unique_user_skill'),
    )
    
    def __repr__(self):
        return f'<Skill {self.user_id}: {self.machine_type} ({self.skill_level})>'

class Vacation(db.Model):
    __tablename__ = 'vacations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    approved = db.Column(db.Boolean, default=False, nullable=False)
    vacation_type = db.Column(db.String(20), default='annual', nullable=False)  # annual, sick, personal
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='valid_vacation_dates'),
        CheckConstraint("vacation_type IN ('annual', 'sick', 'personal', 'emergency')", name='valid_vacation_type'),
        Index('idx_vacation_dates', 'start_date', 'end_date'),
        Index('idx_vacation_user_approved', 'user_id', 'approved'),
    )
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1
    
    def __repr__(self):
        return f'<Vacation {self.id}: User {self.user_id} ({self.start_date} - {self.end_date})>'

# Event listeners for automatic updates
@event.listens_for(Assignment, 'before_update')
def update_assignment_timestamp(mapper, connection, target):
    target.last_status_change = datetime.utcnow()

@event.listens_for(Assignment, 'before_update')
def update_assignment_status_timestamps(mapper, connection, target):
    if target.status == 'in_progress' and not target.started_at:
        target.started_at = datetime.utcnow()
    elif target.status == 'completed' and not target.completed_at:
        target.completed_at = datetime.utcnow()

@event.listens_for(SkillsMatrix, 'before_update')
def update_skills_timestamp(mapper, connection, target):
    target.last_updated = datetime.utcnow() 