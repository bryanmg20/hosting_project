
"""
Lógica de reconstrucción de contenedores existentes.
"""
import os
import tempfile
import subprocess
import shutil
import traceback
from docker import errors as docker_errors
from app.modules.sse.state import _container_name_cache
from app.modules.sse.docker_service import docker_client
from .utils import cleanup_dangling_images


def rebuild_container_logic(container_id, payload):
    """
    Reconstruye el contenedor del proyecto sin borrar el proyecto.
    
    Pasos:
    1. Buscar nombre lógico en cache.
    2. Detener y eliminar contenedor existente (si hay).
    3. Eliminar imagen asociada (por ID y por tag).
    4. Clonar repo / usar contextPath.
    5. Construir nueva imagen (nocache).
    6. Crear nuevo contenedor (sin iniciar).
    7. Limpiar dangling images y tmp dir.
    
    Args:
        container_id: ID del proyecto/contenedor
        payload: Dict con opciones (repoUrl, contextPath, buildArgs, createOptions)
    
    Returns:
        tuple: (response_dict, status_code)
    """
    cache_entry = _container_name_cache.get(container_id)
    if not cache_entry:
        return {
            'success': False,
            'error': 'container_id_not_cached',
            'message': f'No existe entry en cache para id {container_id}. Actualiza lista primero.'
        }, 404

    print(f"[REBUILD][DEBUG] cache_entry={cache_entry!r}", flush=True)

    container_name = cache_entry.get('name') or f'project_{container_id}'
    repo_url = payload.get('repoUrl') or cache_entry.get('githuburl') or ''
    context_path = payload.get('contextPath')
    build_args = payload.get('buildArgs') or {}
    create_kwargs = payload.get('createOptions') or {}

    print(f"[REBUILD][DEBUG] repo_url={repo_url!r}", flush=True)
    print(f"[REBUILD][DEBUG] context_path(before clone)={context_path!r}", flush=True)
    print(f"[REBUILD][DEBUG] build_args={build_args!r}", flush=True)
    print(f"[REBUILD][DEBUG] create_kwargs(initial)={create_kwargs!r}", flush=True)

    # Detener / eliminar contenedor existente
    existing_image_id = None
    try:
        matches = docker_client.containers.list(all=True, filters={'name': container_name})
        if matches:
            existing = matches[0]
            existing_image_id = existing.image.id
            try:
                existing.reload()
                if existing.status == 'running':
                    existing.stop(timeout=10)
                    print(f"[REBUILD] Contenedor {container_name} detenido", flush=True)
            except Exception as e:
                print(f"[REBUILD][WARN] No se pudo detener {container_name}: {e}", flush=True)
            try:
                existing.remove(force=True)
                print(f"[REBUILD] Contenedor {container_name} eliminado", flush=True)
            except docker_errors.APIError as e:
                return {
                    'success': False,
                    'error': 'remove_failed',
                    'message': f'Error eliminando contenedor: {e}'
                }, 500
    except docker_errors.APIError as e:
        return {'success': False, 'error': 'docker_api_error', 'message': str(e)}, 500

    # Eliminar imagen asociada
    if existing_image_id:
        try:
            docker_client.images.remove(existing_image_id, force=True)
            print(f"[REBUILD] Imagen asociada {existing_image_id[:12]} eliminada", flush=True)
        except docker_errors.APIError as e:
            print(f"[REBUILD][WARN] No se pudo eliminar imagen {existing_image_id[:12]}: {e}", flush=True)

    # Eliminar imágenes con tag container_name
    try:
        tagged = docker_client.images.list(name=container_name)
        for img in tagged:
            try:
                docker_client.images.remove(img.id, force=True)
                print(f"[REBUILD] Imagen con tag {img.short_id} eliminada", flush=True)
            except Exception:
                pass
    except Exception:
        pass

    # Clonar repo si no hay context_path
    tmp_dir = None
    if not context_path:
        if repo_url:
            try:
                tmp_dir = tempfile.mkdtemp(prefix=f'{container_name}_rebuild_')
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

    # Build nueva imagen
    try:
        print(f"[REBUILD] Build nueva imagen container_id={container_id} name={container_name} context={context_path}", flush=True)
        
        try:
            image, build_logs = docker_client.images.build(
                path=context_path,
                tag=container_name,
                rm=True,
                buildargs=build_args,
                nocache=True
            )
            print(f"[REBUILD] Build OK image_id={image.id}", flush=True)
        except docker_errors.BuildError as e:
            print(f"[REBUILD][ERROR] BuildError: {e}", flush=True)
            return {
                'success': False,
                'error': 'image_build_error',
                'message': str(e)
            }, 500
        except docker_errors.APIError as e:
            print(f"[REBUILD][ERROR] Docker API error (build): {e}", flush=True)
            return {
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }, 500

        # Crear nuevo contenedor
        print(f"[REBUILD] Creando contenedor para image_id={image.id}", flush=True)
        try:
            print(f"[REBUILD][DEBUG] create_kwargs={create_kwargs!r}", flush=True)
            
            new_container = docker_client.containers.create(
                image.id,
                name=container_name,
                mem_limit="512m",
                memswap_limit="1024m",
                cpu_quota=100000,
                cpu_period=100000,
                network='app-network',
                **create_kwargs
            )
            print(f"[REBUILD] Contenedor creado id={new_container.id}", flush=True)
            cleanup_dangling_images()
            
        except docker_errors.APIError as e:
            print(f"[REBUILD][ERROR] Docker API error (create): {e}", flush=True)
            return {
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }, 500
        except Exception as e:
            print(f"[REBUILD][ERROR] Exception creando contenedor: {e}", flush=True)
            print(traceback.format_exc(), flush=True)
            return {
                'success': False,
                'error': 'container_create_error',
                'message': str(e)
            }, 500

        return {
            'success': True,
            'message': f'Container {container_id} reconstruido (no iniciado)',
            'data': {
                'containerId': container_id,
                'dockerName': container_name,
                'imageId': image.id,
                'createdContainerId': new_container.id,
                'started': False,
                'repoUrl': repo_url or None,
                'rebuilt': True
            }
        }, 200
        
    finally:
        if tmp_dir and os.path.isdir(tmp_dir):
            try:
                shutil.rmtree(tmp_dir)
                print(f"[REBUILD] Limpiado tmp_dir={tmp_dir}", flush=True)
            except Exception as cleanup_err:
                print(f"[REBUILD][WARN] No se pudo limpiar {tmp_dir}: {cleanup_err}", flush=True)
