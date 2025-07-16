from app import create_app, db
from app.models import User, SkillsMatrix, Project, Assignment, Vacation
from datetime import datetime, date, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        print("Starting database seeding...")
        
        # Create admin user
        admin = User(
            email='admin@manufacturing.com',
            username='admin',
            role='admin',
            department_id=1,
            team_id=1,
            hours_per_week=40.0
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
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
            {'username': 'daniel_harris', 'email': 'daniel@manufacturing.com', 'dept': 2, 'team': 4},
            {'username': 'michelle_martin', 'email': 'michelle@manufacturing.com', 'dept': 2, 'team': 4},
        ]
        
        # Team 5: REF machines (non-USA)
        team5_employees = [
            {'username': 'kevin_thompson', 'email': 'kevin@manufacturing.com', 'dept': 2, 'team': 5},
            {'username': 'stephanie_lopez', 'email': 'stephanie@manufacturing.com', 'dept': 2, 'team': 5},
            {'username': 'brian_lee', 'email': 'brian@manufacturing.com', 'dept': 2, 'team': 5},
            {'username': 'nicole_gonzalez', 'email': 'nicole@manufacturing.com', 'dept': 2, 'team': 5},
        ]
        
        # Create all employees
        all_employees = team1_employees + team2_employees + team3_employees + team4_employees + team5_employees
        created_users = []
        
        for emp_data in all_employees:
            employee = User(
                username=emp_data['username'],
                email=emp_data['email'],
                role='employee',
                department_id=emp_data['dept'],
                team_id=emp_data['team'],
                hours_per_week=40.0
            )
            employee.set_password('password123')
            db.session.add(employee)
            created_users.append(employee)
        
        # Commit users first to get their IDs
        db.session.commit()
        
        # Create skills matrix
        skills_data = [
            # Team 1: PAH primary skills
            {'team': 1, 'machine': 'PAH', 'skill': 'primary', 'efficiency': 1.0},
            {'team': 1, 'machine': 'PPH', 'skill': 'secondary', 'efficiency': 0.8},
            
            # Team 2: PPH primary skills (USA)
            {'team': 2, 'machine': 'PPH', 'skill': 'primary', 'efficiency': 1.0},
            {'team': 2, 'machine': 'PAH', 'skill': 'secondary', 'efficiency': 0.7},
            
            # Team 3: PPH primary skills (non-USA)
            {'team': 3, 'machine': 'PPH', 'skill': 'primary', 'efficiency': 1.0},
            {'team': 3, 'machine': 'PAH', 'skill': 'secondary', 'efficiency': 0.7},
            
            # Team 4: REF primary skills (USA)
            {'team': 4, 'machine': 'REF', 'skill': 'primary', 'efficiency': 1.0},
            
            # Team 5: REF primary skills (non-USA)
            {'team': 5, 'machine': 'REF', 'skill': 'primary', 'efficiency': 1.0},
        ]
        
        # Assign skills to users
        for user in created_users:
            for skill_data in skills_data:
                if user.team_id == skill_data['team']:
                    skill = SkillsMatrix(
                        user_id=user.id,
                        machine_type=skill_data['machine'],
                        skill_level=skill_data['skill'],
                        efficiency_factor=skill_data['efficiency']
                    )
                    db.session.add(skill)
        
        # Create sample projects
        sample_projects = [
            {
                'project_number': 'PAH-001-USA',
                'model_type': 'PAH',
                'customer_country': 'USA',
                'difficulty_level': 3,
                'estimated_hours': 40.0,
                'assembly_start_date': date.today() + timedelta(days=30),
                'deadline': date.today() + timedelta(days=16),
                'status': 'unassigned'
            },
            {
                'project_number': 'PPH-002-GER',
                'model_type': 'PPH',
                'customer_country': 'Germany',
                'difficulty_level': 4,
                'estimated_hours': 60.0,
                'assembly_start_date': date.today() + timedelta(days=25),
                'deadline': date.today() + timedelta(days=11),
                'status': 'unassigned'
            },
            {
                'project_number': 'REF-003-USA',
                'model_type': 'REF',
                'customer_country': 'USA',
                'difficulty_level': 2,
                'estimated_hours': 30.0,
                'assembly_start_date': date.today() + timedelta(days=35),
                'deadline': date.today() + timedelta(days=21),
                'status': 'unassigned'
            },
            {
                'project_number': 'APS-004-USA',
                'model_type': 'APS',
                'customer_country': 'USA',
                'difficulty_level': 5,
                'estimated_hours': 80.0,
                'assembly_start_date': date.today() + timedelta(days=40),
                'deadline': date.today() + timedelta(days=26),
                'status': 'unassigned',
                'requires_ref_first': True
            },
            {
                'project_number': 'PSC-005-CAN',
                'model_type': 'PSC',
                'customer_country': 'Canada',
                'difficulty_level': 3,
                'estimated_hours': 45.0,
                'assembly_start_date': date.today() + timedelta(days=28),
                'deadline': date.today() + timedelta(days=14),
                'status': 'unassigned',
                'requires_ref_first': True
            }
        ]
        
        for project_data in sample_projects:
            project = Project(**project_data)
            db.session.add(project)
        
        # Commit all changes
        db.session.commit()
        
        print("Database seeded successfully!")
        print(f"Created admin user: admin@manufacturing.com (password: admin123)")
        print(f"Created {len(created_users)} employees")
        print(f"Created {len(sample_projects)} sample projects")
        print("Employee default password: password123")

if __name__ == '__main__':
    seed_database() 