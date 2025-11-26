import docker
from datetime import datetime
from typing import Dict, List
from app.modules.sse.state import _current_containers
from app.modules.sse.utils import extract_container_name_from_url

# Cliente Docker
docker_client = docker.from_env()

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

def get_containers_metrics(user_email: str) -> List[Dict]:
    """
    Obtener métricas para TODOS los contenedores (running o no)
    """
    metrics_events = []
    containers = _current_containers.get(user_email, [])
    
    for container in containers:
        if not isinstance(container, dict):
            continue
            
        container_id = container.get('_id')
        
        # Obtener nombre directamente de la URL
        url = container.get('url', '')
        container_name = extract_container_name_from_url(url)
        
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
