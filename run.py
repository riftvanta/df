from app import create_app, db
from app.models import User, Project, Assignment, SkillsMatrix, Vacation
import socket

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

def find_free_port(start_port=5000):
    """Find a free port starting from the given port number"""
    port = start_port
    while port < start_port + 100:  # Try up to 100 ports
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise RuntimeError("Could not find a free port")

if __name__ == '__main__':
    try:
        port = find_free_port()
        print(f"Starting Flask app on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except RuntimeError as e:
        print(f"Error: {e}")
        exit(1) 