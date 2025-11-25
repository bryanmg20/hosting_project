from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
import os
import tempfile
import subprocess
import shutil
from docker import errors as docker_errors
import traceback
from app.modules.sse.services.state import _container_name_cache
from app.modules.sse.services.docker_service import docker_client
from app.modules.sse.services.auto_shutdown_service import reset_container_activity
from backend.app.modules.project.responses import error_response
# Nota: No importar delete_project aquí. Rebuild NO elimina el proyecto, sólo reconstruye su contenedor.
container_bp = Blueprint('container', __name__)

# Helper opcional para limpiar imágenes <none> (dangling) tras un build
def _cleanup_dangling_images():
    """Eliminar imágenes dangling (<none>) que quedan tras builds sin etiqueta.
    Se hace de forma best-effort: si falla algún remove se ignora.
    """
    try:
        dangling = docker_client.images.list(filters={'dangling': True})
        removed = 0
        for img in dangling:
            # No remover si (por error) coincide con la imagen recién creada con tag
            try:
                docker_client.images.remove(img.id, force=True)
                removed += 1
            except Exception:
                pass
        print(f"[CREATE][CLEANUP] Dangling images removidas: {removed}", flush=True)
    except Exception as e:
        print(f"[CREATE][CLEANUP][WARN] No se pudo limpiar dangling images: {e}", flush=True)

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
    sub = get_jwt_identity()
    if not sub:
        return error_response('User not authenticated', 401)

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
            # Resetear tracking de inactividad cuando se inicia manualmente
            reset_container_activity(container_name)
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
    sub = get_jwt_identity()
    if not sub:
        return error_response('User not authenticated', 401)
    
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
    """Reconstruye el contenedor del proyecto sin borrar el proyecto.

    Pasos:
    1. Buscar nombre lógico en cache.
    2. Detener y eliminar contenedor existente (si hay).
    3. Eliminar imagen asociada (por ID y por tag).
    4. Clonar repo / usar contextPath igual que create.
    5. Construir nueva imagen (nocache para asegurar reconstrucción real).
    6. Crear (NO iniciar) nuevo contenedor.
    7. Limpiar dangling images y tmp dir.
    8. Responder con datos de nuevo contenedor.
    """
    sub = get_jwt_identity()
    if not sub:
        return error_response('User not authenticated', 401)

    payload = request.get_json(silent=True) or {}
    cache_entry = _container_name_cache.get(container_id)
    if not cache_entry:
        return jsonify({
            'success': False,
            'error': 'container_id_not_cached',
            'message': f'No existe entry en cache para id {container_id}. Actualiza lista primero.'
        }), 404

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

    # 2. Detener / eliminar contenedor existente
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
                return jsonify({
                    'success': False,
                    'error': 'remove_failed',
                    'message': f'Error eliminando contenedor: {e}'
                }), 500
    except docker_errors.APIError as e:
        return jsonify({'success': False, 'error': 'docker_api_error', 'message': str(e)}), 500

    # 3. Eliminar imagen asociada
    if existing_image_id:
        try:
            docker_client.images.remove(existing_image_id, force=True)
            print(f"[REBUILD] Imagen asociada {existing_image_id[:12]} eliminada", flush=True)
        except docker_errors.APIError as e:
            print(f"[REBUILD][WARN] No se pudo eliminar imagen {existing_image_id[:12]}: {e}", flush=True)

    # También eliminar imágenes con tag container_name
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

    # 4. Clonar repo si no hay context_path
    tmp_dir = None
    if not context_path:
        if repo_url:
            try:
                tmp_dir = tempfile.mkdtemp(prefix=f'{container_name}_rebuild_')
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

    # 5. Build nueva imagen
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
            return jsonify({
                'success': False,
                'error': 'image_build_error',
                'message': str(e)
            }), 500
        except docker_errors.APIError as e:
            print(f"[REBUILD][ERROR] Docker API error (build): {e}", flush=True)
            return jsonify({
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }), 500

        # 6. Crear nuevo contenedor (sin iniciar)
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
            _cleanup_dangling_images()
        except docker_errors.APIError as e:
            print(f"[REBUILD][ERROR] Docker API error (create): {e}", flush=True)
            return jsonify({
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }), 500
        except Exception as e:
            print(f"[REBUILD][ERROR] Exception creando contenedor: {e}", flush=True)
            print(traceback.format_exc(), flush=True)
            return jsonify({
                'success': False,
                'error': 'container_create_error',
                'message': str(e)
            }), 500

        return jsonify({
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
        }), 200
    finally:
        if tmp_dir and os.path.isdir(tmp_dir):
            try:
                shutil.rmtree(tmp_dir)
                print(f"[REBUILD] Limpiado tmp_dir={tmp_dir}", flush=True)
            except Exception as cleanup_err:
                print(f"[REBUILD][WARN] No se pudo limpiar {tmp_dir}: {cleanup_err}", flush=True)

    

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
    sub = get_jwt_identity()
    if not sub:
        return error_response('User not authenticated', 401)
    

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
                buildargs=build_args,
                nocache=True
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
            # Limpieza de imágenes dangling (<none>) generadas por el build
            _cleanup_dangling_images()
        except docker_errors.APIError as e:
            print(f"[CREATE][ERROR] Docker API error (create): {e}", flush=True)
            return jsonify({
                'success': False,
                'error': 'docker_api_error',
                'message': str(e)
            }), 500
        except Exception as e:
            print(f"[CREATE][ERROR] Exception creando contenedor: {e}", flush=True)
            import traceback as _tb
            print(_tb.format_exc(), flush=True)
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

