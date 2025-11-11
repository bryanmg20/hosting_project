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
            
            # Obtener estado inicial PERO NO ENVIARLO
            containers = _current_containers.get(user_email, [])
            initial_statuses = {}
            
            # Guardar el estado inicial de cada contenedor
            for container in containers:
                container_id = container.get('id')
                container_name = container.get('container_name', container_id)
                if container_id:
                    initial_status = get_real_container_status(container_name)
                    container['status'] = initial_status
                    initial_statuses[container_id] = initial_status
            
            # Bucle principal de monitoreo - CADA 3 SEGUNDOS
            update_counter = 0
            
            # Variables para trackear el estado anterior
            previous_statuses = initial_statuses.copy()
            previous_metrics = []
            
            while True:
                update_counter += 1
                
                # Actualizar lista de contenedores cada 20 ciclos (≈1 minuto)
                if update_counter % 20 == 0:
                    print(f"🔄 SSE: Updating container list for {user_email}")
                    update_user_containers(user_email)
                    update_counter = 0
                
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
                    yield f"event: {change['event_type']}\n"
                    yield f"data: {json.dumps(change['data'])}\n\n"
                
                # 2. Enviar métricas SOLO para contenedores running y SOLO si hay cambios
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
                
                # Solo imprimir log si hay cambios
                if new_status_changes or new_metrics:
                    print(f"📊 SSE: Sent {len(new_status_changes)} status changes and {len(new_metrics)} metrics updates for {user_email}")
                
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