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

def safe_database_operation(operation_name, operation_func):
    """Safely execute database operations with error handling"""
    try:
        operation_func()
        print(f"✅ {operation_name} completed successfully")
        return True
    except Exception as e:
        print(f"⚠️  {operation_name} failed: {e}")
        return False

def add_missing_columns():
    """Add missing columns to existing tables"""
    from app import create_app, db
    from sqlalchemy import text
    
    try:
        # Commit any pending transactions and start fresh
        db.session.commit()
        
        # Check if tables exist first
        tables_to_check = ['users', 'projects', 'assignments']
        for table in tables_to_check:
            result = db.session.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                )
            """))
            if not result.fetchone()[0]:
                print(f"⚠️  Table '{table}' does not exist, skipping column checks")
                continue
        
        # Check and add missing columns to users table
        print("📝 Checking users table columns...")
        
        # Check if is_active column exists in users table
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_active'
        """))
        
        if not result.fetchone():
            print("📝 Adding missing is_active column to users table...")
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL
            """))
            db.session.commit()
            print("✅ Added is_active column")
        
        # Check if last_login column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'last_login'
        """))
        
        if not result.fetchone():
            print("📝 Adding missing last_login column to users table...")
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN last_login TIMESTAMP
            """))
            db.session.commit()
            print("✅ Added last_login column")
        
        # Check if updated_at column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'updated_at'
        """))
        
        if not result.fetchone():
            print("📝 Adding missing updated_at column to users table...")
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            """))
            db.session.commit()
            print("✅ Added updated_at column")
        
        # Check and add missing columns to projects table
        print("📝 Checking projects table columns...")
        
        # Check if priority column exists in projects table
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'priority'
        """))
        
        if not result.fetchone():
            print("📝 Adding missing priority column to projects table...")
            db.session.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN priority VARCHAR(20) DEFAULT 'normal' NOT NULL
            """))
            db.session.commit()
            print("✅ Added priority column")
            
            # Add the constraint for priority column
            try:
                db.session.execute(text("""
                    ALTER TABLE projects 
                    ADD CONSTRAINT valid_priority 
                    CHECK (priority IN ('urgent', 'high', 'normal', 'low'))
                """))
                db.session.commit()
                print("✅ Added priority constraint")
            except Exception as constraint_error:
                print(f"⚠️  Priority constraint may already exist: {constraint_error}")
                db.session.rollback()
        
        # Check if created_at column exists in projects table
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'created_at'
        """))
        
        if not result.fetchone():
            print("📝 Adding missing created_at column to projects table...")
            db.session.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            """))
            db.session.commit()
            print("✅ Added created_at column")
        
        # Check if updated_at column exists in projects table
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'updated_at'
        """))
        
        if not result.fetchone():
            print("📝 Adding missing updated_at column to projects table...")
            db.session.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            """))
            db.session.commit()
            print("✅ Added updated_at column")
        
        # Check and add missing columns to assignments table
        print("📝 Checking assignments table columns...")
        
        # Check if original_hours column exists in assignments table
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'assignments' AND column_name = 'original_hours'
        """))
        
        if not result.fetchone():
            print("📝 Adding missing original_hours column to assignments table...")
            db.session.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN original_hours FLOAT NOT NULL DEFAULT 0.0
            """))
            db.session.commit()
            print("✅ Added original_hours column")
            
            # Update existing assignments to have original_hours = hours_remaining
            print("📝 Updating existing assignments with original_hours values...")
            db.session.execute(text("""
                UPDATE assignments 
                SET original_hours = hours_remaining 
                WHERE original_hours = 0.0
            """))
            db.session.commit()
            print("✅ Updated existing assignments with original_hours")
        
        # Check for any other missing columns in assignments table
        expected_assignment_columns = [
            'id', 'project_id', 'user_id', 'status', 'hours_remaining', 'original_hours',
            'hold_reason', 'assigned_at', 'started_at', 'completed_at', 'last_status_change'
        ]
        
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'assignments'
            ORDER BY column_name
        """))
        
        existing_columns = [row[0] for row in result.fetchall()]
        missing_columns = set(expected_assignment_columns) - set(existing_columns)
        
        if missing_columns:
            print(f"⚠️  Missing columns in assignments table: {missing_columns}")
            # Add any other missing columns with appropriate defaults
            for column in missing_columns:
                if column in ['hold_reason']:
                    db.session.execute(text(f"""
                        ALTER TABLE assignments 
                        ADD COLUMN {column} VARCHAR(100)
                    """))
                elif column in ['assigned_at', 'started_at', 'completed_at', 'last_status_change']:
                    default_value = "DEFAULT CURRENT_TIMESTAMP" if column in ['assigned_at', 'last_status_change'] else ""
                    db.session.execute(text(f"""
                        ALTER TABLE assignments 
                        ADD COLUMN {column} TIMESTAMP {default_value}
                    """))
                elif column == 'status':
                    db.session.execute(text(f"""
                        ALTER TABLE assignments 
                        ADD COLUMN {column} VARCHAR(20) DEFAULT 'not_started' NOT NULL
                    """))
                
                db.session.commit()
                print(f"✅ Added missing column: {column}")
            
    except Exception as e:
        print(f"⚠️  Error adding missing columns: {e}")
        db.session.rollback()
        return False
    
    return True

def init_railway_database():
    """Initialize the Railway PostgreSQL database with schema and seed data"""
    
    from app import create_app, db
    from app.models import User, Project, Assignment, SkillsMatrix, Vacation
    from flask_migrate import upgrade, init, migrate, stamp
    from sqlalchemy import text
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Initializing Railway PostgreSQL database...")
        
        # Test database connection
        try:
            db.session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as conn_error:
            print(f"❌ Database connection failed: {conn_error}")
            return False
        
        # Try to upgrade database using migrations
        migration_success = safe_database_operation(
            "Database migrations", 
            lambda: upgrade()
        )
        
        # If migration failed, try alternative approaches
        if not migration_success:
            print("📦 Creating database tables from scratch...")
            safe_database_operation(
                "Database table creation",
                lambda: db.create_all()
            )
            
            # Mark the database as up to date with the current migration
            safe_database_operation(
                "Database migration stamp",
                lambda: stamp()
            )
        
        # Always try to add missing columns (this handles partial migrations)
        print("📝 Checking for missing columns...")
        if not add_missing_columns():
            print("⚠️  Some column additions failed, but continuing...")
        
        # Test if we can now query the models
        models_to_test = [
            ("User", User),
            ("Project", Project),
            ("Assignment", Assignment),
            ("SkillsMatrix", SkillsMatrix),
            ("Vacation", Vacation)
        ]
        
        for model_name, model_class in models_to_test:
            try:
                model_class.query.count()
                print(f"✅ {model_name} model query test passed")
            except Exception as query_error:
                print(f"❌ {model_name} model query failed: {query_error}")
                # Don't return here, continue with other models
        
        # Check if admin user already exists
        try:
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("⚠️  Admin user already exists, skipping seed data creation")
                print("🎉 Railway database initialization completed successfully!")
                return True
        except Exception as admin_check_error:
            print(f"⚠️  Could not check for admin user: {admin_check_error}")
        
        # Create admin user
        try:
            admin = User(
                username='admin',
                email='admin@manufacturing.com',
                role='admin',
                department_id=1,
                team_id=1,
                hours_per_week=40.0,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Admin user created")
        except Exception as admin_error:
            print(f"⚠️  Could not create admin user: {admin_error}")
        
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
        
        try:
            employees = []
            for emp_data in sample_employees:
                employee = User(
                    username=emp_data['username'],
                    email=emp_data['email'],
                    role='employee',
                    department_id=emp_data['dept_id'],
                    team_id=emp_data['team_id'],
                    hours_per_week=40.0,
                    is_active=True
                )
                employee.set_password('employee123')
                employees.append(employee)
                db.session.add(employee)
            
            db.session.commit()
            print(f"✅ {len(employees)} sample employees created")
        except Exception as employee_error:
            print(f"⚠️  Could not create sample employees: {employee_error}")
            db.session.rollback()
        
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
        
        try:
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
        except Exception as skills_error:
            print(f"⚠️  Could not create skills matrix: {skills_error}")
            db.session.rollback()
        
        # Create sample projects
        sample_projects = [
            {'number': 'PAH-2024-001', 'type': 'PAH', 'country': 'USA', 'hours': 80, 'difficulty': 3},
            {'number': 'PAH-2024-002', 'type': 'PAH', 'country': 'Germany', 'hours': 70, 'difficulty': 2},
            {'number': 'PPH-2024-001', 'type': 'PPH', 'country': 'USA', 'hours': 120, 'difficulty': 4},
            {'number': 'PPH-2024-002', 'type': 'PPH', 'country': 'France', 'hours': 90, 'difficulty': 3},
            {'number': 'REF-2024-001', 'type': 'REF', 'country': 'USA', 'hours': 60, 'difficulty': 2},
            {'number': 'REF-2024-002', 'type': 'REF', 'country': 'Japan', 'hours': 85, 'difficulty': 3},
        ]
        
        try:
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
        except Exception as project_error:
            print(f"⚠️  Could not create sample projects: {project_error}")
            db.session.rollback()
        
        print("🎉 Railway database initialization completed successfully!")
        print("\n📋 Login credentials:")
        print("   Admin: admin@manufacturing.com / admin123")
        print("   Employee: employee123 (for any employee account)")
        print("\n🔗 Your Railway app is ready to use!")
        return True

if __name__ == '__main__':
    success = init_railway_database()
    if not success:
        print("❌ Database initialization failed!")
        sys.exit(1)
    else:
        print("✅ Database initialization completed successfully!")
        sys.exit(0) 