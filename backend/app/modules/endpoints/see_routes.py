# app/modules/sse/routes/sse_routes.py
from flask import Blueprint, Response, request, jsonify
from flask_jwt_extended import jwt_required, decode_token, get_jwt_identity
from app.modules.sse.services.state import update_user_containers
from app.modules.sse.services.monitor import monitor_containers_events

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
            
            # Usar el nuevo monitor de eventos basado en Docker Events
            for event in monitor_containers_events(user_email):
                yield f"event: {event['event_type']}\n"
                yield f"data: {json.dumps(event['data'])}\n\n"

        except GeneratorExit:
            print(f"SSE: Client disconnected for user {user_email}")
        except Exception as e:
            print(f"Error en SSE: {e}")
            yield f"event: error\n"
            yield f"data: {json.dumps({'message': str(e)})}\n\n"
    
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