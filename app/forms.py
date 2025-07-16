from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, IntegerField, DateField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Length, Optional, Regexp
from wtforms.widgets import TextArea
from app.models import User, Project
from datetime import date, datetime
import re

class LoginForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(), Email(), Length(max=120)], 
                       render_kw={"placeholder": "Enter your email", "autocomplete": "email"})
    password = PasswordField('Password', 
                           validators=[DataRequired(), Length(min=8, max=128)], 
                           render_kw={"placeholder": "Enter your password", "autocomplete": "current-password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=80), 
                                    Regexp(r'^[a-zA-Z0-9_]+$', message='Username must contain only letters, numbers, and underscores')], 
                          render_kw={"placeholder": "Enter username", "autocomplete": "username"})
    email = StringField('Email', 
                       validators=[DataRequired(), Email(), Length(max=120)], 
                       render_kw={"placeholder": "Enter email address", "autocomplete": "email"})
    password = PasswordField('Password', 
                           validators=[DataRequired(), Length(min=8, max=128)], 
                           render_kw={"placeholder": "Enter password", "autocomplete": "new-password"})
    password2 = PasswordField('Repeat Password', 
                            validators=[DataRequired(), EqualTo('password', message='Passwords must match')], 
                            render_kw={"placeholder": "Repeat password", "autocomplete": "new-password"})
    role = SelectField('Role', 
                      choices=[('employee', 'Employee'), ('admin', 'Admin')], 
                      default='employee',
                      validators=[DataRequired()])
    department_id = SelectField('Department', 
                              choices=[('1', 'SM Design'), ('2', 'REF Design')], 
                              coerce=int,
                              validators=[DataRequired()])
    team_id = SelectField('Team', 
                         choices=[
                             ('1', 'Team 1 - PAH (All Countries)'),
                             ('2', 'Team 2 - PPH (USA Only)'),
                             ('3', 'Team 3 - PPH (Non-USA)'),
                             ('4', 'Team 4 - REF (USA Only)'),
                             ('5', 'Team 5 - REF (Non-USA)')
                         ], 
                         coerce=int,
                         validators=[DataRequired()])
    hours_per_week = FloatField('Hours per Week', 
                               validators=[DataRequired(), NumberRange(min=1, max=60)], 
                               default=40.0)
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')
    
    def validate_password(self, password):
        """Enhanced password validation"""
        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password.data):
            raise ValidationError('Password must contain at least one number.')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', 
                               validators=[DataRequired()],
                               render_kw={"placeholder": "Enter current password", "autocomplete": "current-password"})
    new_password = PasswordField('New Password', 
                               validators=[DataRequired(), Length(min=8, max=128)],
                               render_kw={"placeholder": "Enter new password", "autocomplete": "new-password"})
    new_password2 = PasswordField('Confirm New Password', 
                                validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')],
                                render_kw={"placeholder": "Confirm new password", "autocomplete": "new-password"})
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, password):
        """Enhanced password validation for new password"""
        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password.data):
            raise ValidationError('Password must contain at least one number.')

class UpdateProfileForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(), Email(), Length(max=120)], 
                       render_kw={"placeholder": "Enter email address", "autocomplete": "email"})
    hours_per_week = FloatField('Hours per Week', 
                               validators=[DataRequired(), NumberRange(min=1, max=60)], 
                               default=40.0)
    submit = SubmitField('Update Profile')
    
    def validate_email(self, email):
        from flask_login import current_user
        if email.data.lower() != current_user.email:
            user = User.query.filter_by(email=email.data.lower()).first()
            if user:
                raise ValidationError('Email already registered. Please use a different email address.')

class ProjectStatusForm(FlaskForm):
    status = SelectField('Status', 
                        choices=[
                            ('not_started', 'Not Started'),
                            ('in_progress', 'In Progress'),
                            ('on_hold', 'On Hold'),
                            ('completed', 'Completed')
                        ], 
                        validators=[DataRequired()])
    hold_reason = SelectField('Hold Reason', 
                             choices=[
                                 ('', 'Select reason (if on hold)'),
                                 ('waiting_ref_feedback', 'Waiting for REF team feedback'),
                                 ('waiting_electrical_feedback', 'Waiting for electrical team feedback'),
                                 ('working_urgent_project', 'Moving to work on urgent project'),
                                 ('material_shortage', 'Material shortage'),
                                 ('customer_changes', 'Customer requested changes'),
                                 ('technical_issues', 'Technical issues'),
                                 ('waiting_approval', 'Waiting for approval')
                             ])
    hours_remaining = FloatField('Hours Remaining', 
                               validators=[NumberRange(min=0, max=1000)], 
                               render_kw={"placeholder": "Enter remaining hours", "step": "0.1"})
    notes = TextAreaField('Notes', 
                         validators=[Length(max=500)],
                         render_kw={"placeholder": "Optional notes about the status change", "rows": 3})
    submit = SubmitField('Update Status')
    
    def validate_hold_reason(self, hold_reason):
        if self.status.data == 'on_hold' and not hold_reason.data:
            raise ValidationError('Hold reason is required when status is "On Hold".')

class ProjectForm(FlaskForm):
    project_number = StringField('Project Number', 
                                validators=[DataRequired(), Length(min=5, max=50)],
                                render_kw={"placeholder": "Enter project number"})
    model_type = SelectField('Model Type', 
                           choices=[
                               ('PAH', 'PAH'),
                               ('PPH', 'PPH'),
                               ('REF', 'REF'),
                               ('APS', 'APS'),
                               ('PSC', 'PSC')
                           ],
                           validators=[DataRequired()])
    customer_country = StringField('Customer Country', 
                                 validators=[DataRequired(), Length(min=2, max=50)],
                                 render_kw={"placeholder": "Enter customer country"})
    difficulty_level = SelectField('Difficulty Level', 
                                 choices=[
                                     ('1', '1 - Very Easy'),
                                     ('2', '2 - Easy'),
                                     ('3', '3 - Medium'),
                                     ('4', '4 - Hard'),
                                     ('5', '5 - Very Hard')
                                 ],
                                 coerce=int,
                                 validators=[DataRequired()])
    estimated_hours = FloatField('Estimated Hours', 
                               validators=[DataRequired(), NumberRange(min=0.1, max=1000)],
                               render_kw={"placeholder": "Enter estimated hours", "step": "0.1"})
    assembly_start_date = DateField('Assembly Start Date', 
                                   validators=[DataRequired()],
                                   default=date.today)
    deadline = DateField('Deadline', 
                        validators=[DataRequired()],
                        default=date.today)
    priority = SelectField('Priority', 
                         choices=[
                             ('low', 'Low'),
                             ('normal', 'Normal'),
                             ('high', 'High'),
                             ('urgent', 'Urgent')
                         ],
                         default='normal',
                         validators=[DataRequired()])
    requires_ref_first = BooleanField('Requires REF Team First')
    submit = SubmitField('Create Project')
    
    def validate_project_number(self, project_number):
        project = Project.query.filter_by(project_number=project_number.data.upper()).first()
        if project:
            raise ValidationError('Project number already exists. Please use a different number.')
    
    def validate_deadline(self, deadline):
        if deadline.data <= self.assembly_start_date.data:
            raise ValidationError('Deadline must be after assembly start date.')
        if deadline.data <= date.today():
            raise ValidationError('Deadline must be in the future.')

class AssignmentForm(FlaskForm):
    project_id = HiddenField('Project ID', validators=[DataRequired()])
    user_id = SelectField('Assign to Employee', 
                         coerce=int,
                         validators=[DataRequired()],
                         render_kw={"class": "form-control"})
    hours_allocated = FloatField('Hours Allocated', 
                               validators=[DataRequired(), NumberRange(min=0.1, max=1000)],
                               render_kw={"placeholder": "Enter hours to allocate", "step": "0.1"})
    notes = TextAreaField('Assignment Notes', 
                         validators=[Length(max=500)],
                         render_kw={"placeholder": "Optional notes for the assignment", "rows": 3})
    submit = SubmitField('Assign Project')
    
    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        # Populate user choices dynamically
        self.user_id.choices = [(user.id, f"{user.username} - Team {user.team_id}") 
                               for user in User.query.filter_by(role='employee', is_active=True).all()]

class VacationForm(FlaskForm):
    start_date = DateField('Start Date', 
                          validators=[DataRequired()],
                          default=date.today)
    end_date = DateField('End Date', 
                        validators=[DataRequired()],
                        default=date.today)
    vacation_type = SelectField('Vacation Type', 
                              choices=[
                                  ('annual', 'Annual Leave'),
                                  ('sick', 'Sick Leave'),
                                  ('personal', 'Personal Leave'),
                                  ('emergency', 'Emergency Leave')
                              ],
                              default='annual',
                              validators=[DataRequired()])
    notes = TextAreaField('Notes', 
                         validators=[Length(max=500)],
                         render_kw={"placeholder": "Optional notes", "rows": 3})
    submit = SubmitField('Request Vacation')
    
    def validate_end_date(self, end_date):
        if end_date.data < self.start_date.data:
            raise ValidationError('End date must be after start date.')
    
    def validate_start_date(self, start_date):
        if start_date.data < date.today():
            raise ValidationError('Start date cannot be in the past.')

class SkillsForm(FlaskForm):
    user_id = SelectField('Employee', 
                         coerce=int,
                         validators=[DataRequired()])
    machine_type = SelectField('Machine Type', 
                             choices=[
                                 ('PAH', 'PAH'),
                                 ('PPH', 'PPH'),
                                 ('REF', 'REF')
                             ],
                             validators=[DataRequired()])
    skill_level = SelectField('Skill Level', 
                            choices=[
                                ('primary', 'Primary'),
                                ('secondary', 'Secondary')
                            ],
                            validators=[DataRequired()])
    efficiency_factor = FloatField('Efficiency Factor', 
                                 validators=[DataRequired(), NumberRange(min=0.1, max=2.0)],
                                 default=1.0,
                                 render_kw={"step": "0.1"})
    years_experience = IntegerField('Years of Experience', 
                                   validators=[DataRequired(), NumberRange(min=0, max=50)],
                                   default=0)
    submit = SubmitField('Add/Update Skill')
    
    def __init__(self, *args, **kwargs):
        super(SkillsForm, self).__init__(*args, **kwargs)
        # Populate user choices dynamically
        self.user_id.choices = [(user.id, f"{user.username} - Team {user.team_id}") 
                               for user in User.query.filter_by(role='employee', is_active=True).all()]

class FileUploadForm(FlaskForm):
    file = FileField('Upload File', 
                    validators=[DataRequired(), 
                               FileAllowed(['xlsx', 'xls', 'csv'], 'Only Excel and CSV files are allowed!')])
    file_type = SelectField('File Type', 
                           choices=[
                               ('projects', 'Projects'),
                               ('skills', 'Skills Matrix'),
                               ('vacations', 'Vacations'),
                               ('users', 'Users')
                           ],
                           validators=[DataRequired()])
    submit = SubmitField('Upload File')

class SearchForm(FlaskForm):
    search_query = StringField('Search', 
                              validators=[Length(max=100)],
                              render_kw={"placeholder": "Search projects, employees, or assignments..."})
    search_type = SelectField('Search In', 
                             choices=[
                                 ('all', 'All'),
                                 ('projects', 'Projects'),
                                 ('employees', 'Employees'),
                                 ('assignments', 'Assignments')
                             ],
                             default='all')
    submit = SubmitField('Search')

class FilterForm(FlaskForm):
    status = SelectField('Status', 
                        choices=[
                            ('all', 'All Statuses'),
                            ('unassigned', 'Unassigned'),
                            ('assigned', 'Assigned'),
                            ('in_progress', 'In Progress'),
                            ('on_hold', 'On Hold'),
                            ('completed', 'Completed')
                        ],
                        default='all')
    priority = SelectField('Priority', 
                          choices=[
                              ('all', 'All Priorities'),
                              ('low', 'Low'),
                              ('normal', 'Normal'),
                              ('high', 'High'),
                              ('urgent', 'Urgent')
                          ],
                          default='all')
    team_id = SelectField('Team', 
                         choices=[
                             ('all', 'All Teams'),
                             ('1', 'Team 1 - PAH'),
                             ('2', 'Team 2 - PPH (USA)'),
                             ('3', 'Team 3 - PPH (Non-USA)'),
                             ('4', 'Team 4 - REF (USA)'),
                             ('5', 'Team 5 - REF (Non-USA)')
                         ],
                         default='all')
    submit = SubmitField('Filter') 