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
from datetime import datetime

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
        print(f"✅ SSE: Connected user {user_email}")
    except Exception as e:
        print(f"❌ SSE: Invalid token - {e}")
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
            
            # Enviar estado inicial de todos los contenedores
            containers = _current_containers.get(user_email, [])
            for container in containers:
                container_id = container.get('id')
                container_name = container.get('container_name', container_id)
                if container_id:
                    initial_status = get_real_container_status(container_name, container_id)
                    container['status'] = initial_status
                    
                    yield f"event: container_status_changed\n"
                    status_data = json.dumps({
                        'projectId': container_id,
                        'status': initial_status,
                        'previousStatus': initial_status,
                        'name': container.get('name', 'Unknown'),
                        'containerName': container_name,
                        'url': container.get('url', ''),
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    })
                    yield f"data: {status_data}\n\n"
            
            # Bucle principal de monitoreo - CADA 3 SEGUNDOS
            update_counter = 0
            
            while True:
                update_counter += 1
                
                # Actualizar lista de contenedores cada 20 ciclos (≈1 minuto)
                if update_counter % 20 == 0:
                    print(f"🔄 SSE: Updating container list for {user_email}")
                    update_user_containers(user_email)
                    update_counter = 0
                
                # 1. Revisar cambios de estado REALES desde Docker
                status_changes = check_container_changes(user_email)
                for change in status_changes:
                    yield f"event: {change['event_type']}\n"
                    yield f"data: {json.dumps(change['data'])}\n\n"
                
                # 2. Enviar métricas SOLO para contenedores running (simuladas)
                metrics_events = get_containers_metrics(user_email)
                for metrics_event in metrics_events:
                    yield f"event: {metrics_event['event_type']}\n"
                    yield f"data: {json.dumps(metrics_event['data'])}\n\n"
                
                # ESPERAR 3 SEGUNDOS entre revisiones
                time.sleep(3)
                
        except GeneratorExit:
            print(f"🔌 SSE: Client disconnected for user {user_email}")
        except Exception as e:
            print(f"❌ SSE Error in generator for user {user_email}: {e}")
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
    """Handle preflight requests"""
    return '', 200, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Credentials': 'true'
    }