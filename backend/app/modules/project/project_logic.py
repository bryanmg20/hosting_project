import uuid
from datetime import datetime
from app.modules.sse.services.utils import extract_container_name_from_url
from app.modules.sse.services.docker_service import get_real_container_status
def generate_project_id():
    return f"proj-{uuid.uuid4().hex[:8]}"

def generate_project_url(name, username):
    return f"{name}.{username}.localhost"

def format_project_response(container_data, status = "unknown"):
    """Convierte container de Roble a formato"""

    container_name = extract_container_name_from_url(container_data['url'])
    status = get_real_container_status(container_name)
    return {
        'id': container_data['_id'],
        'name': container_data['project_name'],
        'status': status,
        'url': container_data['url'],
        'github_url': container_data['github_url'],
        'created_at': container_data['created_at'],
        'metrics': {'cpu': 0, 'memory': 0, 'requests': 0}
    }

def format_project_list(containers):
    """Convierte lista de containers a formato Figma"""
    return [format_project_response(container) for container in containers]

def create_new_project_data(name, username, github_url):
    """Crea estructura de nuevo proyecto"""
    #project_id = generate_project_id()
    project_url = generate_project_url(name, username)
    created = datetime.utcnow().isoformat() + 'Z'
    
    return {
        'name': name,
        'status': 'unknown',
        'url': project_url,
        'github_url': github_url,
        'created_at': created,
        'metrics': {'cpu': 0, 'memory': 0, 'requests': 0}
    }
