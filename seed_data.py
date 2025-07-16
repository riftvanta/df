from app import create_app, db
from app.models import User, SkillsMatrix, Project, Assignment, Vacation
from datetime import datetime, date, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        print("Starting database seeding...")
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                email='admin@manufacturing.com',
                username='admin',
                role='admin',
                department_id=1,
                team_id=1,
                hours_per_week=40.0,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user")
        else:
            print("Admin user already exists")
        
        # Create sample employees for Department 1 (SM Design)
        # Team 1: PAH machines (all countries)
        team1_employees = [
            {'username': 'john_doe', 'email': 'john@manufacturing.com', 'dept': 1, 'team': 1},
            {'username': 'jane_smith', 'email': 'jane@manufacturing.com', 'dept': 1, 'team': 1},
            {'username': 'mike_wilson', 'email': 'mike@manufacturing.com', 'dept': 1, 'team': 1},
            {'username': 'sarah_jones', 'email': 'sarah@manufacturing.com', 'dept': 1, 'team': 1},
        ]
        
        # Team 2: PPH machines (USA only)
        team2_employees = [
            {'username': 'tom_brown', 'email': 'tom@manufacturing.com', 'dept': 1, 'team': 2},
            {'username': 'lisa_davis', 'email': 'lisa@manufacturing.com', 'dept': 1, 'team': 2},
            {'username': 'mark_garcia', 'email': 'mark@manufacturing.com', 'dept': 1, 'team': 2},
            {'username': 'amy_miller', 'email': 'amy@manufacturing.com', 'dept': 1, 'team': 2},
        ]
        
        # Team 3: PPH machines (non-USA)
        team3_employees = [
            {'username': 'david_wilson', 'email': 'david@manufacturing.com', 'dept': 1, 'team': 3},
            {'username': 'emma_taylor', 'email': 'emma@manufacturing.com', 'dept': 1, 'team': 3},
            {'username': 'chris_anderson', 'email': 'chris@manufacturing.com', 'dept': 1, 'team': 3},
            {'username': 'anna_thomas', 'email': 'anna@manufacturing.com', 'dept': 1, 'team': 3},
        ]
        
        # Department 2 (REF Design)
        # Team 4: REF machines (USA only)
        team4_employees = [
            {'username': 'robert_jackson', 'email': 'robert@manufacturing.com', 'dept': 2, 'team': 4},
            {'username': 'jennifer_white', 'email': 'jennifer@manufacturing.com', 'dept': 2, 'team': 4},
            {'username': 'kevin_harris', 'email': 'kevin@manufacturing.com', 'dept': 2, 'team': 4},
            {'username': 'nicole_martin', 'email': 'nicole@manufacturing.com', 'dept': 2, 'team': 4},
        ]
        
        # Team 5: REF machines (non-USA)
        team5_employees = [
            {'username': 'daniel_thompson', 'email': 'daniel@manufacturing.com', 'dept': 2, 'team': 5},
            {'username': 'michelle_rodriguez', 'email': 'michelle@manufacturing.com', 'dept': 2, 'team': 5},
            {'username': 'jason_lee', 'email': 'jason@manufacturing.com', 'dept': 2, 'team': 5},
            {'username': 'stephanie_walker', 'email': 'stephanie@manufacturing.com', 'dept': 2, 'team': 5},
        ]
        
        # Combine all employee data
        all_employees = team1_employees + team2_employees + team3_employees + team4_employees + team5_employees
        
        # Create employees only if they don't exist
        for emp_data in all_employees:
            existing_user = User.query.filter(
                (User.username == emp_data['username']) | 
                (User.email == emp_data['email'])
            ).first()
            
            if not existing_user:
                user = User(
                    username=emp_data['username'],
                    email=emp_data['email'],
                    role='employee',
                    department_id=emp_data['dept'],
                    team_id=emp_data['team'],
                    hours_per_week=40.0,
                    is_active=True
                )
                user.set_password('employee123')
                db.session.add(user)
                print(f"Created employee: {emp_data['username']}")
            else:
                print(f"Employee {emp_data['username']} already exists (skipping)")
        
        # Commit users first
        try:
            db.session.commit()
            print("Users created successfully")
        except Exception as e:
            print(f"Error creating users: {e}")
            db.session.rollback()
            return
        
        # Create skills matrix
        skills_data = [
            # Team 1 - PAH skills
            {'username': 'john_doe', 'machine': 'PAH', 'level': 'primary', 'efficiency': 1.2, 'experience': 5},
            {'username': 'jane_smith', 'machine': 'PAH', 'level': 'primary', 'efficiency': 1.1, 'experience': 3},
            {'username': 'mike_wilson', 'machine': 'PAH', 'level': 'secondary', 'efficiency': 0.9, 'experience': 2},
            {'username': 'sarah_jones', 'machine': 'PAH', 'level': 'primary', 'efficiency': 1.3, 'experience': 7},
            
            # Team 2 - PPH skills (USA)
            {'username': 'tom_brown', 'machine': 'PPH', 'level': 'primary', 'efficiency': 1.15, 'experience': 4},
            {'username': 'lisa_davis', 'machine': 'PPH', 'level': 'primary', 'efficiency': 1.0, 'experience': 2},
            {'username': 'mark_garcia', 'machine': 'PPH', 'level': 'secondary', 'efficiency': 0.8, 'experience': 1},
            {'username': 'amy_miller', 'machine': 'PPH', 'level': 'primary', 'efficiency': 1.25, 'experience': 6},
            
            # Team 3 - PPH skills (non-USA)
            {'username': 'david_wilson', 'machine': 'PPH', 'level': 'primary', 'efficiency': 1.1, 'experience': 3},
            {'username': 'emma_taylor', 'machine': 'PPH', 'level': 'primary', 'efficiency': 1.0, 'experience': 2},
            {'username': 'chris_anderson', 'machine': 'PPH', 'level': 'secondary', 'efficiency': 0.9, 'experience': 1},
            {'username': 'anna_thomas', 'machine': 'PPH', 'level': 'primary', 'efficiency': 1.2, 'experience': 5},
            
            # Team 4 - REF skills (USA)
            {'username': 'robert_jackson', 'machine': 'REF', 'level': 'primary', 'efficiency': 1.3, 'experience': 8},
            {'username': 'jennifer_white', 'machine': 'REF', 'level': 'primary', 'efficiency': 1.1, 'experience': 4},
            {'username': 'kevin_harris', 'machine': 'REF', 'level': 'secondary', 'efficiency': 0.8, 'experience': 1},
            {'username': 'nicole_martin', 'machine': 'REF', 'level': 'primary', 'efficiency': 1.2, 'experience': 5},
            
            # Team 5 - REF skills (non-USA)
            {'username': 'daniel_thompson', 'machine': 'REF', 'level': 'primary', 'efficiency': 1.1, 'experience': 3},
            {'username': 'michelle_rodriguez', 'machine': 'REF', 'level': 'primary', 'efficiency': 1.0, 'experience': 2},
            {'username': 'jason_lee', 'machine': 'REF', 'level': 'secondary', 'efficiency': 0.9, 'experience': 1},
            {'username': 'stephanie_walker', 'machine': 'REF', 'level': 'primary', 'efficiency': 1.25, 'experience': 6},
        ]
        
        # Create skills matrix entries
        for skill_data in skills_data:
            user = User.query.filter_by(username=skill_data['username']).first()
            if user:
                existing_skill = SkillsMatrix.query.filter_by(
                    user_id=user.id, 
                    machine_type=skill_data['machine']
                ).first()
                
                if not existing_skill:
                    skill = SkillsMatrix(
                        user_id=user.id,
                        machine_type=skill_data['machine'],
                        skill_level=skill_data['level'],
                        efficiency_factor=skill_data['efficiency'],
                        years_experience=skill_data['experience']
                    )
                    db.session.add(skill)
        
        # Create sample projects
        sample_projects = [
            {'number': 'PAH-2024-001', 'type': 'PAH', 'country': 'USA', 'difficulty': 3, 'hours': 120, 'priority': 'normal'},
            {'number': 'PPH-2024-002', 'type': 'PPH', 'country': 'USA', 'difficulty': 4, 'hours': 180, 'priority': 'high'},
            {'number': 'REF-2024-003', 'type': 'REF', 'country': 'Canada', 'difficulty': 2, 'hours': 80, 'priority': 'normal'},
            {'number': 'APS-2024-004', 'type': 'APS', 'country': 'USA', 'difficulty': 5, 'hours': 200, 'priority': 'urgent'},
            {'number': 'PSC-2024-005', 'type': 'PSC', 'country': 'Mexico', 'difficulty': 3, 'hours': 150, 'priority': 'normal'},
            {'number': 'PAH-2024-006', 'type': 'PAH', 'country': 'Germany', 'difficulty': 4, 'hours': 160, 'priority': 'high'},
        ]
        
        for proj_data in sample_projects:
            existing_project = Project.query.filter_by(project_number=proj_data['number']).first()
            if not existing_project:
                # Calculate proper dates
                assembly_start = date.today() + timedelta(days=30)
                # Deadline should be after assembly start date
                deadline = assembly_start + timedelta(days=proj_data['hours'] // 10)  # Rough calculation based on hours
                
                project = Project(
                    project_number=proj_data['number'],
                    model_type=proj_data['type'],
                    customer_country=proj_data['country'],
                    difficulty_level=proj_data['difficulty'],
                    estimated_hours=proj_data['hours'],
                    assembly_start_date=assembly_start,
                    deadline=deadline,
                    priority=proj_data['priority'],
                    requires_ref_first=(proj_data['type'] in ['PPH', 'APS', 'PSC'] and proj_data['country'] == 'USA')
                )
                db.session.add(project)
                print(f"Created project: {proj_data['number']}")
            else:
                print(f"Project {proj_data['number']} already exists (skipping)")
        
        # Commit all changes
        db.session.commit()
        print("Database seeding completed successfully!")
        
        # Print summary
        print(f"\nSummary:")
        print(f"Users: {User.query.count()}")
        print(f"Projects: {Project.query.count()}")
        print(f"Skills: {SkillsMatrix.query.count()}")
        print(f"Admin login: admin@manufacturing.com / admin123")
        print(f"Employee login: john@manufacturing.com / employee123")

if __name__ == '__main__':
    seed_database() 