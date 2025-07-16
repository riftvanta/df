from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Enter username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter email address"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter password"})
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Repeat password"})
    role = SelectField('Role', choices=[('employee', 'Employee'), ('admin', 'Admin')], default='employee')
    department_id = SelectField('Department', choices=[('1', 'SM Design'), ('2', 'REF Design')], coerce=int)
    team_id = SelectField('Team', choices=[
        ('1', 'Team 1 - PAH (All Countries)'),
        ('2', 'Team 2 - PPH (USA Only)'),
        ('3', 'Team 3 - PPH (Non-USA)'),
        ('4', 'Team 4 - REF (USA Only)'),
        ('5', 'Team 5 - REF (Non-USA)')
    ], coerce=int)
    hours_per_week = FloatField('Hours per Week', validators=[DataRequired(), NumberRange(min=1, max=60)], default=40.0)
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class ProjectStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed')
    ], validators=[DataRequired()])
    hold_reason = SelectField('Hold Reason', choices=[
        ('', 'Select reason (if on hold)'),
        ('waiting_ref_feedback', 'Waiting for REF team feedback'),
        ('waiting_electrical_feedback', 'Waiting for electrical team feedback'),
        ('working_urgent_project', 'Moving to work on urgent project'),
        ('material_shortage', 'Material shortage'),
        ('customer_changes', 'Customer requested changes')
    ])
    hours_remaining = FloatField('Hours Remaining', validators=[NumberRange(min=0)], render_kw={"placeholder": "Enter remaining hours"})
    submit = SubmitField('Update Status') 