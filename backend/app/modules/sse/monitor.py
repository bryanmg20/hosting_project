import queue
import threading
import time
import docker
from datetime import datetime
from app.modules.sse.state import _current_containers
from app.modules.sse.utils import extract_container_name_from_url
from app.modules.sse.docker_service import get_containers_metrics

def monitor_containers_events(user_email: str):
    """
    Generador que escucha eventos de Docker y emite actualizaciones SSE.
    Reemplaza el polling constante.
    """
    event_queue = queue.Queue()
    stop_event = threading.Event()
    
    # Función para reconstruir el mapa de contenedores del usuario
    def get_user_container_map():
        c_map = {}
        containers = _current_containers.get(user_email, [])
        for c in containers:
            cid = c.get('_id')
            if cid:
                # Obtener nombre directamente de la URL del contenedor en _current_containers
                # Esto asegura que solo procesamos contenedores que pertenecen al usuario
                url = c.get('url', '')
                cname = extract_container_name_from_url(url)
                
                if cname:
                    c_map[cname] = cid
        return c_map

    def docker_event_listener():
        """Hilo que consume eventos de Docker"""
        try:
            # Filtrar eventos de contenedores
            # decode=True devuelve dicts
            # filters={'type': 'container'} reduce el ruido
            client = docker.from_env() # Cliente local para el hilo
            for event in client.events(decode=True, filters={'type': 'container'}):
                if stop_event.is_set():
                    break
                
                # Filtrar solo eventos relevantes
                if event.get('Action') in ['start', 'die', 'create', 'destroy', 'pause', 'unpause']:
                    event_queue.put(event)
        except Exception as e:
            print(f"Error en listener de eventos Docker: {e}")

    # Iniciar hilo daemon
    t = threading.Thread(target=docker_event_listener, daemon=True)
    t.start()

    last_metrics_time = 0
    metrics_interval = 2 # Segundos

    try:
        while True:
            # Calcular timeout para el próximo envío de métricas
            now = time.time()
            time_since_metrics = now - last_metrics_time
            timeout = max(0.1, metrics_interval - time_since_metrics)

            try:
                # Esperar evento o timeout
                event = event_queue.get(timeout=timeout)
                
                # Procesar evento Docker
                attr = event.get('Actor', {}).get('Attributes', {})
                docker_name = attr.get('name')
                
                # Obtener mapa actualizado (por si hubo creaciones)
                container_map = get_user_container_map()
                project_id = container_map.get(docker_name)
                
                if project_id:
                    action = event.get('Action')
                    new_status = 'unknown'
                    
                    if action == 'start' or action == 'unpause':
                        new_status = 'running'
                    elif action == 'die' or action == 'stop' or action == 'kill':
                        new_status = 'exited'
                    elif action == 'create':
                        new_status = 'created' # o created
                    elif action == 'pause':
                        new_status = 'inactive'
                    elif action == 'destroy':
                        new_status = 'removing'
                    
                    # Actualizar estado en memoria
                    containers = _current_containers.get(user_email, [])
                    for c in containers:
                        if c.get('_id') == project_id:
                            c['status'] = new_status
                            break

                    # Emitir evento de cambio de estado
                    yield {
                        'event_type': 'container_status_changed',
                        'data': {
                            'projectId': project_id,
                            'status': new_status,
                            'projectName': docker_name,
                            'timestamp': datetime.utcnow().isoformat() + 'Z'
                        }
                    }
                    
            except queue.Empty:
                # Timeout alcanzado, continuar para métricas
                pass
            
            # Enviar métricas si pasó el tiempo
            if time.time() - last_metrics_time >= metrics_interval:
                metrics_events = get_containers_metrics(user_email)
                for m in metrics_events:
                    yield m
                last_metrics_time = time.time()

    finally:
        stop_event.set()
