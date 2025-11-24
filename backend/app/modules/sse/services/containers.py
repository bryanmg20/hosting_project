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
    Actualizar la lista de contenedores desde la base de datos usando project_service
    """
    try:
        from app.modules.auth.services.project_service import project_service
        
        containers_result = project_service.get_user_projects(user_email)
       
        if containers_result['success']:
            containers = containers_result.get('projects', [])
         
            # Extraer y cachear nombres de contenedores desde las URLs
            for container in containers:
                container_id = container.get('_id')
                container_url = container.get('url', '')
                githuburl = container.get('github_url', '')
                # Extraer nombre del contenedor desde la URL
                container_name = extract_container_name_from_url(container_url)

                _container_name_cache[container_id] = {
                    "name": container_name,
                    "githuburl": githuburl
                }
               
            
            _current_containers[user_email] = containers
         
            return True
        else:
           
            return False
            
    except Exception as e:
        
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
        # Normalizar estados para la UI
        if status == 'created':
            status = 'inactive'  # contenedor existe pero no está iniciado
        
     
        return status
        
    except docker.errors.NotFound:
       
        return 'unknown'
    except docker.errors.APIError as e:
     
        return 'unknown'
    except Exception as e:
       
        return 'unknown'

def get_container_metrics(container_name: str) -> Dict:
    """
    Obtener métricas REALES del contenedor usando Docker stats.
    - cpu: porcentaje de uso CPU aproximado
    - memory: uso de memoria (MB)
    - requests: se aproxima usando paquetes RX (si existe red) como indicador
    - uptime: tiempo desde que inició el contenedor
    - lastActivity: timestamp actual UTC
    """
    try:
        status = get_real_container_status(container_name)
        
        if status != 'running':
            return {
                'cpu': 0,
                'memory': 0, 
                'requests': 0,
                'uptime': "0h 0m",
                'lastActivity': datetime.utcnow().isoformat() + 'Z'
            }
        # Obtener contenedor real
        containers = docker_client.containers.list(all=True, filters={'name': container_name})
        if not containers:
            return {
                'cpu': 0,
                'memory': 0,
                'requests': 0,
                'uptime': "0h 0m",
                'lastActivity': datetime.utcnow().isoformat() + 'Z'
            }
        container = containers[0]

        # Stats del contenedor (stream=False para única lectura)
        stats = container.stats(stream=False)

        # Calcular CPU % (delta basado en precpu)
        cpu_percent = 0.0
        try:
            cpu_stats = stats.get('cpu_stats', {})
            precpu_stats = stats.get('precpu_stats', {})
            cpu_usage = cpu_stats.get('cpu_usage', {})
            pre_cpu_usage = precpu_stats.get('cpu_usage', {})
            total_usage = cpu_usage.get('total_usage', 0)
            pre_total_usage = pre_cpu_usage.get('total_usage', 0)
            system_cpu_usage = cpu_stats.get('system_cpu_usage', 0)
            pre_system_cpu_usage = precpu_stats.get('system_cpu_usage', 0)
            cpu_delta = total_usage - pre_total_usage
            system_delta = system_cpu_usage - pre_system_cpu_usage
            online_cpus = cpu_stats.get('online_cpus') or len(cpu_usage.get('percpu_usage', []) or []) or 1
            if cpu_delta > 0 and system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0
        except Exception:
            cpu_percent = 0.0

        # Calcular memoria (MB)
        mem_mb = 0
        try:
            mem_stats = stats.get('memory_stats', {})
            mem_usage = mem_stats.get('usage', 0)
            mem_mb = int(mem_usage / (1024 * 1024))
        except Exception:
            mem_mb = 0

        # Requests aproximados: usar paquetes recibidos totales de redes
        requests_count = 0
        try:
            networks = stats.get('networks', {})
            for net_name, net_vals in networks.items():
                requests_count += net_vals.get('rx_packets', 0)
        except Exception:
            requests_count = 0

        # Uptime: calcular desde StartedAt
        uptime_str = "0h 0m"
        try:
            started_at = container.attrs.get('State', {}).get('StartedAt')
            if started_at:
                # Formato ISO con Z y posible nanosegundos. Cortar para strptime.
                # Ej: '2025-11-23T18:22:33.123456789Z'
                clean = started_at.rstrip('Z')
                # Limitar microsegundos a 6 dígitos
                if '.' in clean:
                    date_part, frac = clean.split('.')
                    clean = f"{date_part}.{frac[:6]}"
                from datetime import timezone
                try:
                    started_dt = datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    try:
                        started_dt = datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S')
                    except ValueError:
                        started_dt = datetime.utcnow()
                started_dt = started_dt.replace(tzinfo=timezone.utc)
                now = datetime.utcnow().replace(tzinfo=timezone.utc)
                delta = now - started_dt
                hours = delta.seconds // 3600 + delta.days * 24
                minutes = (delta.seconds % 3600) // 60
                uptime_str = f"{hours}h {minutes}m"
        except Exception:
            uptime_str = "0h 0m"

        return {
            'cpu': round(cpu_percent, 2),
            'memory': mem_mb,
            'requests': requests_count,
            'uptime': uptime_str,
            'lastActivity': datetime.utcnow().isoformat() + 'Z'
        }
        
    except Exception as e:
      
        return {
            'cpu': 0,
            'memory': 0,
            'requests': 0,
            'uptime': "0h 0m",
            'lastActivity': datetime.utcnow().isoformat() + 'Z'
        }

def check_container_changes(user_email: str, previous_statuses: Dict[str, str] = None) -> List[Dict]:
    """
    Revisar todos los contenedores del usuario y detectar cambios REALES
    """
    changes = []
    containers = _current_containers.get(user_email, [])
    
    for container in containers:
        container_id = container.get('_id')
        container_name = _container_name_cache.get(container_id, container_id).get('name', container_id)
        
        if not container_id:
            continue
            
        # Obtener estado ACTUAL desde Docker REAL
        current_status = get_real_container_status(container_name)
        
        # ✅ USAR previous_statuses si se proporciona, sino usar el interno
        if previous_statuses is not None:
            previous_status = previous_statuses.get(container_id, 'unknown')
        else:
            previous_status = container.get('status', 'unknown')
        
        # Solo si hay cambio de estado REAL
        if previous_status != current_status:
        

            changes.append({
                'event_type': 'container_status_changed',
                'data': {
                    'projectId': container_id,
                    'status': current_status,
                    'previousStatus': previous_status or 'unknown',
                    'projectName': container.get('project_name', 'Unknown'),
                    'url': container.get('url', ''),
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            })
            
            # Actualizar AMBOS: el estado interno Y previous_statuses si se proporciona
            container['status'] = current_status
            if previous_statuses is not None:
                previous_statuses[container_id] = current_status
    
    return changes

# app/modules/sse/services/container_status_service.py

def get_containers_metrics(user_email: str) -> List[Dict]:
    """
    Obtener métricas para TODOS los contenedores (running o no)
    """
    metrics_events = []
    containers = _current_containers.get(user_email, [])
    
    for container in containers:
        container_id = container.get('_id')
        container_name = _container_name_cache.get(container_id, container_id).get('name', container_id)
        
        if container_id:
            # Obtener métricas sin importar el estado
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