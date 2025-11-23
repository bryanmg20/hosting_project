# app/modules/sse/routes/sse_routes.py
from flask import Blueprint, Response, request, jsonify
from flask_jwt_extended import jwt_required, decode_token, get_jwt_identity
from app.modules.sse.services.containers import (
    update_user_containers,
    check_container_changes,
    get_containers_metrics,
    _current_containers,
    get_real_container_status
)
import json
import time

sse_bp = Blueprint('sse', __name__)

@sse_bp.route('/containers/events')
def sse_events():
    """SSE endpoint para eventos en tiempo real - consulta Docker real"""
    token = request.args.get('token')
    if not token:
        return "Token required", 401
    try:
        decoded_token = decode_token(token)
        user_email = decoded_token['sub']

    except Exception as e:
        return "Invalid token", 401
    
    def generate_events():
        try:
            # Actualización inicial de contenedores
            if not update_user_containers(user_email):
                yield f"event: container_error\n"
                error_data = json.dumps({
                    'message': 'Failed to fetch user containers',
                    'error_code': 'CONTAINERS_FETCH_ERROR'
                })
                yield f"data: {error_data}\n\n"
                
                return
            
            # Evento de conexión exitosa
            yield f"event: connected\n"
            connected_data = json.dumps({
                'message': 'SSE connected successfully',
                'userEmail': user_email
            })
            yield f"data: {connected_data}\n\n"
            
            # Obtener estado inicial PERO NO ENVIARLO
            containers = _current_containers.get(user_email, [])
            initial_statuses = {}
            
            # Guardar el estado inicial de cada contenedor
            for container in containers:
                container_id = container.get('_id')
               
                if container_id:
                    initial_status = 'unknown'
                    container['status'] = initial_status
                    initial_statuses[container_id] = initial_status
            
            # Variables para trackear el estado anterior
            previous_statuses = initial_statuses.copy()
            previous_metrics = []
            
            while True:
                # 1. Revisar cambios de estado REALES desde Docker
                current_status_changes = check_container_changes(user_email)
                
                # Filtrar solo los cambios que son diferentes al estado anterior
                new_status_changes = []
                for change in current_status_changes:
                    container_id = change['data'].get('projectId')
                    current_status = change['data'].get('status')
                    previous_status = previous_statuses.get(container_id)
                    
                    # Solo enviar si el estado cambió
                    if current_status != previous_status:
                        new_status_changes.append(change)
                        # Actualizar el estado anterior
                        previous_statuses[container_id] = current_status
                
                # Enviar solo los cambios nuevos
                for change in new_status_changes:
                    #print(change, flush=True)
                    yield f"event: {change['event_type']}\n"
                    yield f"data: {json.dumps(change['data'])}\n\n"
                
                # 2. Enviar métricas para todos los contenedores
                current_metrics = get_containers_metrics(user_email)
                
                # Filtrar solo las métricas que son diferentes a las anteriores
                new_metrics = []
                for metric in current_metrics:
                    if metric not in previous_metrics:
                        new_metrics.append(metric)
                
                # Enviar solo las métricas nuevas
                for metrics_event in new_metrics:
                    yield f"event: {metrics_event['event_type']}\n"
                    yield f"data: {json.dumps(metrics_event['data'])}\n\n"
                
                # Actualizar el estado anterior de métricas
                previous_metrics = current_metrics
                
    
                # ESPERAR 3 SEGUNDOS entre revisiones
                time.sleep(2)
                
        except GeneratorExit:
            print(f"SSE: Client disconnected for user {user_email}")
        except Exception as e:
            print(f"SSE Error in generator for user {user_email}: {e}")
            yield f"event: container_error\n"
            error_data = json.dumps({
                'message': str(e),
                'error_code': 'GENERATOR_ERROR'
            })
            yield f"data: {error_data}\n\n"
    
    return Response(
        generate_events(), 
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Credentials': 'true'
        }
    )

# Endpoint para forzar actualización manual
@sse_bp.route('/containers/refresh', methods=['POST'])
@jwt_required()
def refresh_containers():
    """Forzar actualización de la lista de contenedores"""
    try:
        user_email = get_jwt_identity()
        
        if update_user_containers(user_email):
            return jsonify({
                'success': True,
                'message': 'Containers list updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update containers list'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@sse_bp.route('/containers/events', methods=['OPTIONS'])
def sse_options():
    """Handle preflight requests with proper validation"""
    
    # Configuración desde variables de entorno
    allowed_origins = 'http://ui.localhost' #current_app.config.get('CORS_ALLOWED_ORIGINS', [])
    origin = request.headers.get('Origin', '')
    
    # Validar origen
    if origin not in allowed_origins:
        return 'Origin not allowed', 403, {
            'Access-Control-Allow-Origin': 'null'  # Origen no permitido
        }
    
    # Validar método
    if request.method != 'OPTIONS':
        return 'Method not allowed', 405
    
    headers = {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '86400',  # Cache por 24h
    }

    
    return '', 200, headers