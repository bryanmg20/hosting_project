
"""
Lógica de construcción y creación de contenedores Docker.
"""
import os
import tempfile
import subprocess
import shutil
import traceback as _tb
from docker import errors as docker_errors
from app.modules.sse.docker_service import docker_client
from app.modules.auth.services.project_service import project_service
from app.modules.sse.utils import extract_container_name_from_url
from .utils import cleanup_dangling_images


def create_container_logic(container_id, payload, user_email):
    """
    Construye la imagen Docker del proyecto y crea el contenedor.
    
    Args:
        container_id: ID del proyecto/contenedor
        payload: Dict con opciones (repoUrl, contextPath, buildArgs, createOptions)
        user_email: Email del usuario autenticado
    
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
    repo_url = payload.get('repoUrl') or project.get('github_url') or ''
    context_path = payload.get('contextPath')
    build_args = payload.get('buildArgs') or {}

    # Clonar repo si no se especifica context_path
    tmp_dir = None
    if not context_path:
        if repo_url:
            try:
                tmp_dir = tempfile.mkdtemp(prefix=f'{container_name}_')
                subprocess.check_call(['git', 'clone', '--depth', '1', repo_url, tmp_dir])
                context_path = tmp_dir
            except subprocess.CalledProcessError as e:
                return {
                    'success': False,
                    'error': 'git_clone_failed',
                    'message': f'Error clonando repo {repo_url}: {e}'
                }, 400
        else:
            return {
                'success': False,
                'error': 'no_context',
                'message': 'Debe proporcionar contextPath o repoUrl.'
            }, 400

    if not os.path.isdir(context_path):
        return {
            'success': False,
            'error': 'invalid_context_path',
            'message': f'Ruta de build inválida: {context_path}'
        }, 400

    try:
        print(f"[CREATE] Iniciando build container_id={container_id} name={container_name} context={context_path}", flush=True)
        
        # Build imagen
        try:
            image, build_logs = docker_client.images.build(
                path=context_path,
                tag=container_name,
                rm=True,
                buildargs=build_args,
                nocache=True
            )
            print(f"[CREATE] Build OK image_id={image.id}", flush=True)
        except docker_errors.BuildError as e:
            print(f"[CREATE][ERROR] BuildError: {e}", flush=True)
            return {
                'success': False,
                'error': 'image_build_error',
                'message': str(e)
            }, 500
        except docker_errors.APIError as e:
            print(f"[CREATE][ERROR] Docker API error (build): {e}", flush=True)
            return {
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }, 500

        # Remover contenedor previo con mismo nombre
        try:
            existing = docker_client.containers.list(all=True, filters={'name': container_name})
            for c in existing:
                try:
                    c.remove(force=True)
                except Exception:
                    pass
        except docker_errors.APIError:
            pass

        # Crear nuevo contenedor
        print(f"[CREATE] Creando contenedor para image_id={image.id}", flush=True)
        try:
            create_kwargs = payload.get('createOptions') or {}
            print(f"[CREATE][DEBUG] create_kwargs={create_kwargs!r}", flush=True)
            
            container_obj = docker_client.containers.create(
                image.id,
                name=container_name,
                mem_limit="512m",
                memswap_limit="1024m",
                cpu_quota=100000,
                cpu_period=100000,
                network='app-network',
                **create_kwargs
            )
            print(f"[CREATE] Contenedor creado id={container_obj.id}", flush=True)
            cleanup_dangling_images()
            
        except docker_errors.APIError as e:
            print(f"[CREATE][ERROR] Docker API error (create): {e}", flush=True)
            return {
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }, 500
        except Exception as e:
            print(f"[CREATE][ERROR] Exception creando contenedor: {e}", flush=True)
            print(_tb.format_exc(), flush=True)
            return {
                'success': False,
                'error': 'container_create_error',
                'message': str(e)
            }, 500

        return {
            'success': True,
            'message': f'Container {container_id} creado (no iniciado)',
            'data': {
                'containerId': container_id,
                'dockerName': container_name,
                'imageId': image.id,
                'createdContainerId': container_obj.id,
                'started': False,
                'repoUrl': repo_url or None
            }
        }, 201
    
    finally:
        if tmp_dir and os.path.isdir(tmp_dir):
            try:
                shutil.rmtree(tmp_dir)
                print(f"[CREATE] Limpiado tmp_dir={tmp_dir}", flush=True)
            except Exception as cleanup_err:
                print(f"[CREATE][WARN] No se pudo limpiar {tmp_dir}: {cleanup_err}", flush=True)
