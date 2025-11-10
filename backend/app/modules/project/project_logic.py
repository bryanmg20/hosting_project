import uuid
from datetime import datetime

def generate_project_id():
    return f"proj-{uuid.uuid4().hex[:8]}"

def generate_project_url(name, username):
    return f"{name}.{username}.localhost"

def format_project_response(container_data, status='running'):
    """Convierte container de Roble a formato Figma"""
    return {
        'id': container_data['id'],
        'name': container_data['name'],
        'status': status,
        'url': container_data['url'],
        'template': container_data['template'],
        'github_url': container_data['github_url'],
        'created_at': container_data['created_at'],
        'metrics': {'cpu': 0, 'memory': 0, 'requests': 0}
    }

def format_project_list(containers):
    """Convierte lista de containers a formato Figma"""
    return [format_project_response(container, 'unknown') for container in containers]

def create_new_project_data(name, username, template, github_url):
    """Crea estructura de nuevo proyecto"""
    project_id = generate_project_id()
    project_url = generate_project_url(name, username)
    created = datetime.utcnow().isoformat() + 'Z'
    
    return {
        'id': project_id,
        'name': name,
        'status': 'deploying',
        'url': project_url,
        'template': template,
        'github_url': github_url,
        'created_at': created,
        'metrics': {'cpu': 0, 'memory': 0, 'requests': 0}
    }