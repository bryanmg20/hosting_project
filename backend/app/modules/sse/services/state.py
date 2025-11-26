from typing import Dict, List
from app.modules.sse.services.utils import extract_container_name_from_url

# Estado global para persistencia
_current_containers = {}  # {user_email: [container_list]}

def update_user_containers(user_email: str) -> bool:
    """
    Actualizar la lista de contenedores desde la base de datos usando project_service
    """
    try:
        from app.modules.auth.services.project_service import project_service
        
        containers_result = project_service.get_user_projects(user_email)
       
        if containers_result['success']:
            containers = containers_result.get('projects', [])
            _current_containers[user_email] = containers
            return True
        else:
            return False
            
    except Exception as e:
        return False

def reset_states():
    """Resetear estados"""
    global _current_containers
    _current_containers = {}
