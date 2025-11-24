from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import os
import tempfile
import subprocess
import shutil
from docker import errors as docker_errors
from app.modules.sse.services.containers import _container_name_cache, docker_client
container_bp = Blueprint('container', __name__)

# Helper opcional para limpiar imágenes "dangling" (<none>) generadas por builds multi-stage
def _auto_prune_dangling_images():
    if os.environ.get('AUTO_PRUNE_DANGLING', '0') != '1':
        return
    print('[PRUNE] Iniciando prune de imágenes dangling...', flush=True)
    try:
        result = docker_client.images.prune(filters={'dangling': True})
        deleted = result.get('ImagesDeleted') or []
        reclaimed = result.get('SpaceReclaimed')
        print(f"[PRUNE] Eliminadas={len(deleted)} SpaceReclaimed={reclaimed} bytes", flush=True)
    except docker_errors.APIError as e:
        print(f"[PRUNE][ERROR] Docker API error: {e}", flush=True)
    except Exception as e:
        print(f"[PRUNE][ERROR] Exception: {e}", flush=True)

@container_bp.route('/containers/<container_id>/start', methods=['POST'])
@jwt_required()
def start_container(container_id):
    """
    Inicia un contenedor previamente creado.

    Flujo:
    1. Obtiene el nombre lógico desde _container_name_cache.
    2. Busca el contenedor real en Docker.
    3. Si está detenido -> start()
    4. Devuelve estado.
    """

    cache_entry = _container_name_cache.get(container_id)
    if not cache_entry:
        return jsonify({
            'success': False,
            'error': 'container_id_not_cached',
            'message': f'No existe entry en cache para id {container_id}.'
        }), 404

    container_name = cache_entry.get('name') or f'project_{container_id}'

    # Buscar contenedor por nombre
    try:
        containers = docker_client.containers.list(all=True, filters={'name': container_name})
        if not containers:
            return jsonify({
                'success': False,
                'error': 'container_not_found',
                'message': f'No existe contenedor con nombre {container_name}'
            }), 404

        container_obj = containers[0]

        # Iniciar si está detenido
        if container_obj.status != 'running':
            container_obj.start()
            message = f'Container {container_name} iniciado correctamente'
        else:
            message = f'Container {container_name} ya estaba en ejecución'

        container_obj.reload()

        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'containerId': container_id,
                'dockerName': container_name,
                'state': container_obj.status
            }
        }), 200

    except docker_errors.APIError as e:
        return jsonify({
            'success': False,
            'error': 'docker_api_error',
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'start_failed',
            'message': str(e)
        }), 500

@container_bp.route('/containers/<container_id>/stop', methods=['POST'])
@jwt_required()
def stop_container(container_id):
    """
    Detiene un contenedor previamente creado y/o iniciado.
    """
    cache_entry = _container_name_cache.get(container_id)
    if not cache_entry:
        return jsonify({
            'success': False,
            'error': 'container_id_not_cached',
            'message': f'No existe entry en cache para id {container_id}.'
        }), 404

    container_name = cache_entry.get('name') or f'project_{container_id}'

    try:
        # Buscar contenedor por nombre
        containers = docker_client.containers.list(all=True, filters={'name': container_name})
        if not containers:
            return jsonify({
                'success': False,
                'error': 'container_not_found',
                'message': f'No existe contenedor con nombre {container_name}'
            }), 404

        container_obj = containers[0]

        # Detener si está corriendo
        if container_obj.status == 'running':
            container_obj.stop()
            message = f'Container {container_name} detenido correctamente'
        else:
            message = f'Container {container_name} ya estaba detenido'

        container_obj.reload()

        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'containerId': container_id,
                'dockerName': container_name,
                'state': container_obj.status
            }
        }), 200

    except docker_errors.APIError as e:
        return jsonify({
            'success': False,
            'error': 'docker_api_error',
            'message': str(e)
        }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'stop_failed',
            'message': str(e)
        }), 500

@container_bp.route('/containers/<container_id>/rebuild', methods=['POST'])
@jwt_required()
def restart_container(container_id):
    """Reinicia un contenedor: stop -> remove -> create -> start"""

    # 1. Buscar en cache
    cache_entry = _container_name_cache.get(container_id)
    if not cache_entry:
        return jsonify({
            'success': False,
            'error': 'container_id_not_cached',
            'message': f'No existe entry en cache para id {container_id}.'
        }), 404

    container_name = cache_entry.get('name') or f'project_{container_id}'

    # 2. Buscar contenedor existente
    try:
        matches = docker_client.containers.list(all=True, filters={'name': container_name})
        if not matches:
            return jsonify({
                'success': False,
                'error': 'container_not_found',
                'message': f'No existe contenedor con nombre {container_name}'
            }), 404

        container = matches[0]
    except docker_errors.APIError as e:
        return jsonify({'success': False, 'error': 'docker_api_error', 'message': str(e)}), 500

    # 3. Detener contenedor si está corriendo
    try:
        container.reload()
        if container.status == 'running':
            container.stop()
    except Exception:
        pass

    # 4. Eliminar contenedor
    try:
        container.remove(force=True)
    except docker_errors.APIError as e:
        return jsonify({
            'success': False,
            'error': 'remove_failed',
            'message': f'Error eliminando contenedor: {e}'
        }), 500

    # 5. Crear nuevo contenedor desde la misma imagen
    try:
        image_id = container.image.id
        new_container = docker_client.containers.create(
            image=image_id,
            name=container_name,
            user = "viewer", 
            network='app-network'
        )
    except docker_errors.APIError as e:
        return jsonify({'success': False, 'error': 'recreate_failed', 'message': str(e)}), 500

    # 6. Iniciar contenedor
    try:
        new_container.start()
        new_container.reload()
    except docker_errors.APIError as e:
        return jsonify({'success': False, 'error': 'start_failed', 'message': str(e)}), 500

    # 7. Resultado
    return jsonify({
        'success': True,
        'message': f'Container {container_id} reiniciado correctamente',
        'data': {
            'containerId': container_id,
            'dockerName': container_name,
            'newContainerId': new_container.id,
            'status': new_container.status
        }
    }), 200

@container_bp.route('/containers/<container_id>/create', methods=['POST'])
@jwt_required()
def create_container(container_id):
    """Construye la imagen Docker del proyecto y crea/ejecuta el contenedor.

    Flujo:
    1. Busca en _container_name_cache el nombre lógico y githuburl del proyecto.
    2. Opcionalmente recibe JSON: {"repoUrl": str, "contextPath": str, "buildArgs": {..}}.
       - Si se pasa contextPath se usa como directorio de build.
       - Si no hay contextPath pero hay repoUrl (o githuburl cacheada) se clona shallow en tmp.
    3. Construye la imagen: tag = container_name
    4. Elimina contenedor previo con mismo nombre (si existe) y crea uno nuevo detached.
    5. Devuelve id de imagen y contenedor.
    """
    

    payload = request.get_json(silent=True) or {}
    cache_entry = _container_name_cache.get(container_id)
    if not cache_entry:
        return jsonify({
            'success': False,
            'error': 'container_id_not_cached',
            'message': f'No existe entry en cache para id {container_id}. Actualiza lista primero.'
        }), 404

    container_name = cache_entry.get('name') or f'project_{container_id}'
    repo_url = payload.get('repoUrl') or cache_entry.get('githuburl') or ''
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
                return jsonify({
                    'success': False,
                    'error': 'git_clone_failed',
                    'message': f'Error clonando repo {repo_url}: {e}'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'no_context',
                'message': 'Debe proporcionar contextPath o repoUrl.'
            }), 400

    if not os.path.isdir(context_path):
        return jsonify({
            'success': False,
            'error': 'invalid_context_path',
            'message': f'Ruta de build inválida: {context_path}'
        }), 400

    # Construir imagen y limpiar tmp_dir tras build
    try:
        print(f"[CREATE] Iniciando build container_id={container_id} name={container_name} context={context_path}", flush=True)
        try:
            image, build_logs = docker_client.images.build(
                path=context_path,
                tag=container_name,
                rm=True,
                buildargs=build_args
            )
            print(f"[CREATE] Build OK image_id={image.id}", flush=True)
        except docker_errors.BuildError as e:
            print(f"[CREATE][ERROR] BuildError: {e}", flush=True)
            return jsonify({
                'success': False,
                'error': 'image_build_error',
                'message': str(e)
            }), 500
        except docker_errors.APIError as e:
            print(f"[CREATE][ERROR] Docker API error (build): {e}", flush=True)
            return jsonify({
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }), 500

        # Remover contenedor previo con mismo nombre
        try:
            existing = docker_client.containers.list(all=True, filters={'name': container_name})
            for c in existing:
                try:
                    c.remove(force=True)
                except Exception:
                    pass
        except docker_errors.APIError:
            # No bloquea creación si falla listado
            pass

        # Crear (pero NO iniciar) nuevo contenedor
        print(f"[CREATE] Creando contenedor para image_id={image.id}", flush=True)
        try:
            create_kwargs = payload.get('createOptions') or {}
            container_obj = docker_client.containers.create(image.id, name=container_name, network='app-network',  **create_kwargs)
            print(f"[CREATE] Contenedor creado id={container_obj.id}", flush=True)
        except docker_errors.APIError as e:
            print(f"[CREATE][ERROR] Docker API error (create): {e}", flush=True)
            return jsonify({
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }), 500
        except Exception as e:
            print(f"[CREATE][ERROR] Exception creando contenedor: {e}", flush=True)
            return jsonify({
                'success': False,
                'error': 'container_create_error',
                'message': str(e)
            }), 500

        return jsonify({
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
        }), 201
    
    finally:
        # Limpiar directorio temporal clonado (si existe)
        if tmp_dir and os.path.isdir(tmp_dir):
            try:
                shutil.rmtree(tmp_dir)
                print(f"[CREATE] Limpiado tmp_dir={tmp_dir}", flush=True)
            except Exception as cleanup_err:
                print(f"[CREATE][WARN] No se pudo limpiar {tmp_dir}: {cleanup_err}", flush=True)
        # Prune de imágenes dangling (si habilitado)
        _auto_prune_dangling_images()

