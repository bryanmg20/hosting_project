
"""
Operaciones de ciclo de vida de contenedores: start, stop.
"""
from flask import jsonify
from docker import errors as docker_errors
from app.modules.sse.services.state import _container_name_cache
from app.modules.sse.services.docker_service import docker_client
from app.modules.sse.services.auto_shutdown_service import reset_container_activity


def start_container_logic(container_id):
    """
    Lógica para iniciar un contenedor previamente creado.
    
    Returns:
        tuple: (response_dict, status_code)
    """
    cache_entry = _container_name_cache.get(container_id)
    if not cache_entry:
        return {
            'success': False,
            'error': 'container_id_not_cached',
            'message': f'No existe entry en cache para id {container_id}.'
        }, 404

    container_name = cache_entry.get('name') or f'project_{container_id}'

    try:
        containers = docker_client.containers.list(all=True, filters={'name': container_name})
        if not containers:
            return {
                'success': False,
                'error': 'container_not_found',
                'message': f'No existe contenedor con nombre {container_name}'
            }, 404

        container_obj = containers[0]

        if container_obj.status != 'running':
            container_obj.start()
            message = f'Container {container_name} iniciado correctamente'
            reset_container_activity(container_name)
        else:
            message = f'Container {container_name} ya estaba en ejecución'

        container_obj.reload()

        return {
            'success': True,
            'message': message,
            'data': {
                'containerId': container_id,
                'dockerName': container_name,
                'state': container_obj.status
            }
        }, 200

    except docker_errors.APIError as e:
        return {
            'success': False,
            'error': 'docker_api_error',
            'message': str(e)
        }, 500
    except Exception as e:
        return {
            'success': False,
            'error': 'start_failed',
            'message': str(e)
        }, 500


def stop_container_logic(container_id):
    """
    Lógica para detener un contenedor previamente creado y/o iniciado.
    
    Returns:
        tuple: (response_dict, status_code)
    """
    cache_entry = _container_name_cache.get(container_id)
    if not cache_entry:
        return {
            'success': False,
            'error': 'container_id_not_cached',
            'message': f'No existe entry en cache para id {container_id}.'
        }, 404

    container_name = cache_entry.get('name') or f'project_{container_id}'

    try:
        containers = docker_client.containers.list(all=True, filters={'name': container_name})
        if not containers:
            return {
                'success': False,
                'error': 'container_not_found',
                'message': f'No existe contenedor con nombre {container_name}'
            }, 404

        container_obj = containers[0]

        if container_obj.status == 'running':
            container_obj.stop()
            message = f'Container {container_name} detenido correctamente'
        else:
            message = f'Container {container_name} ya estaba detenido'

        container_obj.reload()

        return {
            'success': True,
            'message': message,
            'data': {
                'containerId': container_id,
                'dockerName': container_name,
                'state': container_obj.status
            }
        }, 200

    except docker_errors.APIError as e:
        return {
            'success': False,
            'error': 'docker_api_error',
            'message': str(e)
        }, 500
    except Exception as e:
        return {
            'success': False,
            'error': 'stop_failed',
            'message': str(e)
        }, 500
