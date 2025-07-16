#!/usr/bin/env python3
"""
Railway Database Initialization Script
This script sets up the database schema and creates initial data for Railway deployment.
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Project, Assignment, SkillsMatrix, Vacation

def init_railway_database():
    """Initialize the Railway PostgreSQL database with schema and seed data"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Initializing Railway PostgreSQL database...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("⚠️  Admin user already exists, skipping seed data creation")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@manufacturing.com',
            role='admin',
            department_id=1,
            team_id=1,
            hours_per_week=40.0
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("✅ Admin user created")
        
        # Create sample employees
        sample_employees = [
            # SM Design Department - Team 1 (PAH machines)
            {'username': 'john_pah', 'email': 'john@manufacturing.com', 'team_id': 1, 'dept_id': 1},
            {'username': 'mary_pah', 'email': 'mary@manufacturing.com', 'team_id': 1, 'dept_id': 1},
            
            # SM Design Department - Team 2 (PPH USA)
            {'username': 'bob_pph_usa', 'email': 'bob@manufacturing.com', 'team_id': 2, 'dept_id': 1},
            {'username': 'alice_pph_usa', 'email': 'alice@manufacturing.com', 'team_id': 2, 'dept_id': 1},
            
            # SM Design Department - Team 3 (PPH non-USA)
            {'username': 'charlie_pph_intl', 'email': 'charlie@manufacturing.com', 'team_id': 3, 'dept_id': 1},
            {'username': 'diana_pph_intl', 'email': 'diana@manufacturing.com', 'team_id': 3, 'dept_id': 1},
            
            # REF Design Department - Team 4 (REF USA)
            {'username': 'eve_ref_usa', 'email': 'eve@manufacturing.com', 'team_id': 4, 'dept_id': 2},
            {'username': 'frank_ref_usa', 'email': 'frank@manufacturing.com', 'team_id': 4, 'dept_id': 2},
            
            # REF Design Department - Team 5 (REF non-USA)
            {'username': 'grace_ref_intl', 'email': 'grace@manufacturing.com', 'team_id': 5, 'dept_id': 2},
            {'username': 'henry_ref_intl', 'email': 'henry@manufacturing.com', 'team_id': 5, 'dept_id': 2},
        ]
        
        employees = []
        for emp_data in sample_employees:
            employee = User(
                username=emp_data['username'],
                email=emp_data['email'],
                role='employee',
                department_id=emp_data['dept_id'],
                team_id=emp_data['team_id'],
                hours_per_week=40.0
            )
            employee.set_password('employee123')
            employees.append(employee)
            db.session.add(employee)
        
        db.session.commit()
        print(f"✅ {len(employees)} sample employees created")
        
        # Create skills matrix
        skills_data = [
            # PAH team skills
            {'username': 'john_pah', 'machine_type': 'PAH', 'skill_level': 'primary', 'efficiency': 1.2},
            {'username': 'mary_pah', 'machine_type': 'PAH', 'skill_level': 'primary', 'efficiency': 1.1},
            
            # PPH USA team skills
            {'username': 'bob_pph_usa', 'machine_type': 'PPH', 'skill_level': 'primary', 'efficiency': 1.0},
            {'username': 'alice_pph_usa', 'machine_type': 'PPH', 'skill_level': 'primary', 'efficiency': 1.15},
            
            # PPH International team skills
            {'username': 'charlie_pph_intl', 'machine_type': 'PPH', 'skill_level': 'primary', 'efficiency': 1.1},
            {'username': 'diana_pph_intl', 'machine_type': 'PPH', 'skill_level': 'primary', 'efficiency': 1.0},
            
            # REF USA team skills
            {'username': 'eve_ref_usa', 'machine_type': 'REF', 'skill_level': 'primary', 'efficiency': 1.0},
            {'username': 'frank_ref_usa', 'machine_type': 'REF', 'skill_level': 'primary', 'efficiency': 1.05},
            
            # REF International team skills
            {'username': 'grace_ref_intl', 'machine_type': 'REF', 'skill_level': 'primary', 'efficiency': 1.1},
            {'username': 'henry_ref_intl', 'machine_type': 'REF', 'skill_level': 'primary', 'efficiency': 1.0},
        ]
        
        for skill_data in skills_data:
            user = User.query.filter_by(username=skill_data['username']).first()
            if user:
                skill = SkillsMatrix(
                    user_id=user.id,
                    machine_type=skill_data['machine_type'],
                    skill_level=skill_data['skill_level'],
                    efficiency_factor=skill_data['efficiency']
                )
                db.session.add(skill)
        
        db.session.commit()
        print("✅ Skills matrix created")
        
        # Create sample projects
        sample_projects = [
            {'number': 'PAH-2024-001', 'type': 'PAH', 'country': 'USA', 'hours': 80, 'difficulty': 3},
            {'number': 'PAH-2024-002', 'type': 'PAH', 'country': 'Germany', 'hours': 70, 'difficulty': 2},
            {'number': 'PPH-2024-001', 'type': 'PPH', 'country': 'USA', 'hours': 120, 'difficulty': 4},
            {'number': 'PPH-2024-002', 'type': 'PPH', 'country': 'France', 'hours': 90, 'difficulty': 3},
            {'number': 'REF-2024-001', 'type': 'REF', 'country': 'USA', 'hours': 60, 'difficulty': 2},
            {'number': 'REF-2024-002', 'type': 'REF', 'country': 'Japan', 'hours': 85, 'difficulty': 3},
        ]
        
        for proj_data in sample_projects:
            # Calculate dates
            start_date = date.today() + timedelta(days=7)
            deadline = start_date + timedelta(days=21)  # 3 weeks later
            
            # Determine if REF is required first
            requires_ref = (
                (proj_data['type'] == 'PPH' and proj_data['country'] == 'USA') or
                proj_data['type'] in ['APS', 'PSC']
            )
            
            project = Project(
                project_number=proj_data['number'],
                model_type=proj_data['type'],
                customer_country=proj_data['country'],
                difficulty_level=proj_data['difficulty'],
                estimated_hours=proj_data['hours'],
                assembly_start_date=start_date,
                deadline=deadline,
                requires_ref_first=requires_ref,
                status='unassigned'
            )
            db.session.add(project)
        
        db.session.commit()
        print("✅ Sample projects created")
        
        print("🎉 Railway database initialization completed successfully!")
        print("\n📋 Login credentials:")
        print("   Admin: admin@manufacturing.com / admin123")
        print("   Employee: employee123 (for any employee account)")
        print("\n🔗 Your Railway app is ready to use!")

if __name__ == '__main__':
    init_railway_database() 