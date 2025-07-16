from app import create_app, db
from app.models import User, Project, Assignment, SkillsMatrix, Vacation

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Project': Project,
        'Assignment': Assignment,
        'SkillsMatrix': SkillsMatrix,
        'Vacation': Vacation
    }

if __name__ == '__main__':
    app.run() 