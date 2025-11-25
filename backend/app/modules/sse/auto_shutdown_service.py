# app/modules/sse/services/auto_shutdown_service.py
import docker
import time
import threading
from datetime import datetime
from typing import Dict

# Cliente Docker
docker_client = docker.from_env()

# Estado de monitoreo: {container_name: {'last_rx_bytes': int, 'last_activity_time': timestamp, 'inactive_since': timestamp}}
_activity_tracker = {}
_tracker_lock = threading.Lock()

# Configuración
# Tiempo de inactividad permitido antes de detener el contenedor (30 minutos)
INACTIVITY_THRESHOLD_SECONDS = 1800  # 1800 segundos

# Intervalo entre cada chequeo del monitor (10 minutos)
CHECK_INTERVAL_SECONDS = 10  # 10 segundos

# Flag para detener el servicio
_shutdown_flag = False

# Contenedores de infraestructura que NO deben ser detenidos por inactividad
INFRASTRUCTURE_CONTAINERS = {
    'hosting_project-backend-1',
    'hosting_project-ui-1', 
    'hosting_project-nginx-1',
    'backend-1',
    'ui-1',
    'nginx-1'
}


def is_user_project_container(container_name: str) -> bool:
    """
    Verifica si un contenedor es de un proyecto de usuario (no infraestructura).
    Los contenedores de infraestructura se excluyen del auto-shutdown.
    """
    # Excluir contenedores de infraestructura por nombre exacto
    if container_name in INFRASTRUCTURE_CONTAINERS:
        return False
    
    # Excluir contenedores que empiecen con 'hosting_project-'
    if container_name.startswith('hosting_project-'):
        return False
    
    return True


def get_container_network_stats(container_name: str) -> int:
    """
    Obtiene los bytes recibidos totales (rx_bytes) del contenedor.
    Retorna 0 si el contenedor no está running o no hay stats.
    """
    try:
        containers = docker_client.containers.list(all=True, filters={'name': container_name})
        if not containers:
            return 0
        
        container = containers[0]
        if container.status.lower() != 'running':
            return 0
        
        stats = container.stats(stream=False)
        networks = stats.get('networks', {})
        total_rx_bytes = 0
        for net_name, net_vals in networks.items():
            total_rx_bytes += net_vals.get('rx_bytes', 0)
        
        return total_rx_bytes
    except Exception as e:
        print(f"[AUTO_SHUTDOWN][ERROR] No se pudieron obtener stats para {container_name}: {e}", flush=True)
        return 0


def check_and_stop_inactive_containers():
    """
    Revisa contenedores de proyectos de usuario y detiene los que llevan 
    INACTIVITY_THRESHOLD_SECONDS sin actividad de red.
    Excluye contenedores de infraestructura (backend, ui, nginx).
    """
    try:
        # Obtener todos los contenedores running
        running_containers = docker_client.containers.list(filters={'status': 'running'})
        
        current_time = time.time()
        
        for container in running_containers:
            container_name = container.name
            
            # Saltar contenedores de infraestructura
            if not is_user_project_container(container_name):
                #print(f"[AUTO_SHUTDOWN] Saltando contenedor de infraestructura: {container_name}", flush=True)
                continue
            
            # Obtener rx_bytes actual
            current_rx_bytes = get_container_network_stats(container_name)
            
            with _tracker_lock:
                # Si es la primera vez que vemos este contenedor
                if container_name not in _activity_tracker:
                    _activity_tracker[container_name] = {
                        'last_rx_bytes': current_rx_bytes,
                        'last_activity_time': current_time,
                        'inactive_since': None
                    }
                    print(f"[AUTO_SHUTDOWN] Tracking iniciado para {container_name}", flush=True)
                    continue
                
                tracker = _activity_tracker[container_name]
                last_rx = tracker['last_rx_bytes']
                
                # Detectar si hubo actividad (cambio en rx_bytes)
                if current_rx_bytes != last_rx:
                    # Hay actividad
                    tracker['last_rx_bytes'] = current_rx_bytes
                    tracker['last_activity_time'] = current_time
                    tracker['inactive_since'] = None
                    print(f"[AUTO_SHUTDOWN] Actividad detectada en {container_name} (rx: {current_rx_bytes})", flush=True)
                else:
                    # No hay actividad
                    if tracker['inactive_since'] is None:
                        # Primera vez sin actividad
                        tracker['inactive_since'] = current_time
                        print(f"[AUTO_SHUTDOWN] {container_name} sin actividad detectada", flush=True)
                    else:
                        # Ya estaba inactivo, verificar tiempo
                        inactive_duration = current_time - tracker['inactive_since']
                        
                        if inactive_duration >= INACTIVITY_THRESHOLD_SECONDS:
                            print(f"[AUTO_SHUTDOWN] {container_name} inactivo por {inactive_duration:.0f}s. Deteniendo...", flush=True)
                            try:
                                container.stop(timeout=10)
                                print(f"[AUTO_SHUTDOWN] {container_name} detenido por inactividad", flush=True)
                                # Limpiar del tracker
                                del _activity_tracker[container_name]
                            except Exception as e:
                                print(f"[AUTO_SHUTDOWN][ERROR] No se pudo detener {container_name}: {e}", flush=True)
                        else:
                            remaining = INACTIVITY_THRESHOLD_SECONDS - inactive_duration
                            print(f"[AUTO_SHUTDOWN] {container_name} inactivo por {inactive_duration:.0f}s (quedan {remaining:.0f}s)", flush=True)
    
    except Exception as e:
        print(f"[AUTO_SHUTDOWN][ERROR] Error en check_and_stop_inactive_containers: {e}", flush=True)


def auto_shutdown_monitor():
    """
    Thread principal que ejecuta el monitoreo periódico.
    """
    print(f"[AUTO_SHUTDOWN] Servicio iniciado. Umbral: {INACTIVITY_THRESHOLD_SECONDS}s, Intervalo: {CHECK_INTERVAL_SECONDS}s", flush=True)
    
    while not _shutdown_flag:
        check_and_stop_inactive_containers()
        time.sleep(CHECK_INTERVAL_SECONDS)
    
    print("[AUTO_SHUTDOWN] Servicio detenido", flush=True)


def start_auto_shutdown_service():
    """
    Inicia el servicio de auto-apagado en un thread daemon.
    """
    global _shutdown_flag
    _shutdown_flag = False
    
    monitor_thread = threading.Thread(target=auto_shutdown_monitor, daemon=True, name="AutoShutdownMonitor")
    monitor_thread.start()
    print("[AUTO_SHUTDOWN] Thread de monitoreo iniciado", flush=True)


def stop_auto_shutdown_service():
    """
    Detiene el servicio de auto-apagado.
    """
    global _shutdown_flag
    _shutdown_flag = True
    print("[AUTO_SHUTDOWN] Señal de detención enviada", flush=True)


def reset_container_activity(container_name: str):
    """
    Resetea el tracking de actividad para un contenedor específico.
    Útil cuando se inicia manualmente un contenedor.
    """
    with _tracker_lock:
        if container_name in _activity_tracker:
            del _activity_tracker[container_name]
            print(f"[AUTO_SHUTDOWN] Tracking reseteado para {container_name}", flush=True)
