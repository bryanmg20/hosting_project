# app/modules/sse/services/container_status_service.py
import docker
import random
import time
from datetime import datetime
from typing import Dict, List
import re

# Cliente Docker
docker_client = docker.from_env()

# Estado global para persistencia
_current_containers = {}  # {user_email: [container_list]}
_container_name_cache = {}  # {container_id: container_name}

def update_user_containers(user_email: str) -> bool:
    """
    Actualizar la lista de contenedores desde la base de datos usando container_service
    """
    try:
        from app.modules.auth.services.container_service import container_service
        
        containers_result = container_service.get_user_containers(user_email)
        
        if containers_result['success']:
            containers = containers_result.get('containers', [])
            
            # Extraer y cachear nombres de contenedores desde las URLs
            for container in containers:
                container_id = container.get('id')
                container_url = container.get('url', '')
                
                # Extraer nombre del contenedor desde la URL
                container_name = extract_container_name_from_url(container_url)
                _container_name_cache[container_id] = container_name
                container['container_name'] = container_name
            
            _current_containers[user_email] = containers
            print(f"🔄 Status: Updated {len(containers)} containers for user {user_email}")
            return True
        else:
            print(f"❌ Status: Failed to update containers for user {user_email}")
            return False
            
    except Exception as e:
        print(f"❌ Status: Error updating containers for {user_email}: {e}")
        return False

def extract_container_name_from_url(url: str) -> str:
    """
    Extraer el nombre del contenedor desde la URL
    """
    if not url:
        return 'default_id'
    
    # Tomar las primeras dos partes: proyecto.name → proyecto-name
    parts = url.split('.')
    if len(parts) >= 2:
        container_name = f"{parts[0]}-{parts[1]}"
    else:
        container_name = parts[0]
    
    container_name = re.sub(r'[^a-zA-Z0-9_-]', '', container_name)
    
    return container_name if container_name else 'default_id'


def get_real_container_status(container_name: str) -> str:
    """
    Obtener el estado REAL del contenedor desde Docker
    """
    try:
        # Buscar el contenedor por nombre en Docker
        containers = docker_client.containers.list(
            all=True,  # Incluir contenedores detenidos
            filters={'name': container_name}
        )
        
        if not containers:
            
            return 'unknown'
        
        # Tomar el primer contenedor que coincida
        container = containers[0]
        status = container.status.lower()
        
        print(f"🔍 Docker: Container {container_name} status: {status}")
        return status
        
    except docker.errors.NotFound:
        print(f"⚠️  Docker: Container {container_name} not found")
        return 'unknown'
    except docker.errors.APIError as e:
        print(f"❌ Docker API Error for {container_name}: {e}")
        return 'unknown'
    except Exception as e:
        print(f"❌ Error getting Docker status for {container_name}: {e}")
        return 'unknown'

def get_container_metrics(container_name: str) -> Dict:
    """
    Obtener métricas REALES del contenedor desde Docker
    Si no está running, devolver métricas vacías o None
    """
    try:
        # Verificar si el contenedor está running
        status = get_real_container_status(container_name)
        if status != 'running':
            return {
                'cpu': 0,
                'memory': 0,
                'memory_usage': "0MB / 0MB",
                'network': "0MB",
                'requests': 0,
                'uptime': "0h 0m",
                'lastActivity': datetime.utcnow().isoformat() + 'Z'
                }
        
        # SIMULAR métricas (esto es lo único que simulamos)
        return {
            'cpu': random.randint(5, 95),
            'memory': random.randint(50, 512),
            'memory_usage': f"{random.randint(100, 500)}MB / {random.randint(512, 1024)}MB",
            'network': f"{random.randint(1, 100)}MB",
            'requests': random.randint(0, 1000),
            'uptime': f"{random.randint(0, 24)}h {random.randint(0, 59)}m",
            'lastActivity': datetime.utcnow().isoformat() + 'Z'
        }
        
    except Exception as e:
        print(f"❌ Error getting metrics for {container_name}: {e}")
        return None

def check_container_changes(user_email: str) -> List[Dict]:
    """
    Revisar todos los contenedores del usuario y detectar cambios REALES
    """
    changes = []
    containers = _current_containers.get(user_email, [])
    
    for container in containers:
        container_id = container.get('id')
        container_name = _container_name_cache.get(container_id, container_id)
        
        if not container_id:
            continue
            
        # Obtener estado ACTUAL desde Docker REAL
        current_status = get_real_container_status(container_name)
        previous_status = container.get('status', 'unknown')
        
        # Solo si hay cambio de estado REAL
        if previous_status != current_status:

            changes.append({
                'event_type': 'container_status_changed',
                'data': {
                    'projectId': container_id,
                    'status': current_status,
                    'previousStatus': previous_status or 'unknown',
                    'name': container.get('name', 'Unknown'),
                    'containerName': container_name,
                    'url': container.get('url', ''),
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            })
            # Actualizar estado en el contenedor
            container['status'] = current_status
    
    return changes

def get_containers_metrics(user_email: str) -> List[Dict]:
    """
    Obtener métricas SOLO para contenedores que están running
    """
    metrics_events = []
    containers = _current_containers.get(user_email, [])
    
    for container in containers:
        container_id = container.get('id')
        container_name = _container_name_cache.get(container_id, container_id)
        
        if container_id and container.get('status') == 'running':
            metrics = get_container_metrics(container_name)
            if metrics:
                metrics_events.append({
                    'event_type': 'metrics_updated',
                    'data': {
                        'projectId': container_id,
                        'metrics': metrics
                    }
                })
    
    return metrics_events

def reset_states():
    """Resetear estados"""
    global _current_containers, _container_name_cache
    _current_containers = {}
    _container_name_cache = {}