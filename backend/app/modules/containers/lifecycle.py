
"""
Operaciones de ciclo de vida de contenedores: start, stop.
"""
from flask import jsonify
from docker import errors as docker_errors
from app.modules.sse.docker_service import docker_client
from app.modules.sse.auto_shutdown_service import reset_container_activity
from app.modules.auth.services.project_service import project_service
from app.modules.sse.utils import extract_container_name_from_url


def start_container_logic(container_id, user_email):
    """
    Lógica para iniciar un contenedor previamente creado.
    
    Returns:
        tuple: (response_dict, status_code)
    """
    # Obtener detalles del proyecto
    project_result = project_service.get_project_by_id(user_email, container_id)
    if not project_result['success']:
        return {
            'success': False,
            'error': 'project_not_found',
            'message': f'No existe proyecto con id {container_id}.'
        }, 404

    project = project_result['project']
    container_name = extract_container_name_from_url(project.get('url'))

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


def stop_container_logic(container_id, user_email):
    """
    Lógica para detener un contenedor previamente creado y/o iniciado.
    
    Returns:
        tuple: (response_dict, status_code)
    """
    # Obtener detalles del proyecto
    project_result = project_service.get_project_by_id(user_email, container_id)
    if not project_result['success']:
        return {
            'success': False,
            'error': 'project_not_found',
            'message': f'No existe proyecto con id {container_id}.'
        }, 404

    project = project_result['project']
    container_name = extract_container_name_from_url(project.get('url'))

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
