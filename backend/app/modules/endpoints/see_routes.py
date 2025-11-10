from flask import Blueprint, Response, request, jsonify
from flask_jwt_extended import jwt_required, decode_token
from app.modules.auth.services.container_service import container_service
import json
import time
import random
from datetime import datetime

sse_bp = Blueprint('sse', __name__)

def get_real_container_status(container_id: str) -> str:
    """
    Obtener el estado REAL del contenedor desde Docker
    Por ahora es un mock, pero después se conectará a Docker real
    """
    try:
        # Mock temporal - simular estados basados en probabilidad
        status_probability = random.random()
        if status_probability < 0.7:  # 70% running
            return 'running'
        elif status_probability < 0.85:  # 15% stopped
            return 'stopped'
        elif status_probability < 0.95:  # 10% restarting
            return 'error'
        else:  # 5% error
            return 'error'
    except Exception as e:
        print(f"❌ Error getting container status for {container_id}: {e}")
        return 'unknown'

@sse_bp.route('/containers/events')
def sse_events():
    """SSE endpoint para eventos en tiempo real con proyectos REALES del usuario"""
    
    # Verificar token JWT
    token = request.args.get('token')
    if not token:
        return "Token required", 401
    
    try:
        # Decodificar y verificar el token JWT
        decoded_token = decode_token(token)
        user_email = decoded_token['sub']
        print(f"✅ SSE: Connected user {user_email}")
    except Exception as e:
        print(f"❌ SSE: Invalid token - {e}")
        return "Invalid token", 401
    
    def generate_events():
        try:
            # Obtener proyectos REALES del usuario
            containers_result = container_service.get_user_containers(user_email)
            
            if not containers_result['success']:
                yield f"event: container_error\n"
                error_data = json.dumps({
                    'message': 'Failed to fetch user containers',
                    'error_code': 'CONTAINERS_FETCH_ERROR'
                })
                yield f"data: {error_data}\n\n"
                return
            
            real_containers = containers_result.get('containers', [])
            print(f"📋 SSE: User {user_email} has {len(real_containers)} containers")
            
            # Evento de conexión exitosa con info de containers
            yield f"event: connected\n"
            connected_data = json.dumps({
                'message': f'SSE connected for {len(real_containers)} containers',
                'containerCount': len(real_containers),
                'userEmail': user_email
            })
            yield f"data: {connected_data}\n\n"
            
            # Enviar estado inicial de todos los contenedores
            for container in real_containers:
                container_id = container.get('id')
                if container_id:
                    real_status = get_real_container_status(container_id)
                    yield f"event: container_status_changed\n"
                    status_data = json.dumps({
                        'projectId': container_id,
                        'status': real_status,
                        'previousStatus': 'unknown',
                        'name': container.get('name', 'Unknown'),
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    })
                    yield f"data: {status_data}\n\n"
            
            # Monitorear cambios en tiempo real
            event_id = 0
            previous_states = {}
            
            while True:
                event_id += 1
                
                # Para cada contenedor real, verificar si hay cambios
                for container in real_containers:
                    container_id = container.get('id')
                    if not container_id:
                        continue
                    
                    # Obtener estado actual (mock por ahora)
                    current_status = get_real_container_status(container_id)
                    previous_status = previous_states.get(container_id)
                    
                    # Solo enviar evento si el estado cambió
                    if previous_status != current_status:
                        yield f"event: container_status_changed\n"
                        change_data = json.dumps({
                            'projectId': container_id,
                            'status': current_status,
                            'previousStatus': previous_status or 'unknown',
                            'name': container.get('name', 'Unknown'),
                            'timestamp': datetime.utcnow().isoformat() + 'Z'
                        })
                        yield f"data: {change_data}\n\n"
                        
                        previous_states[container_id] = current_status
                
                # También enviar métricas periódicamente para contenedores running
                for container in real_containers:
                    container_id = container.get('id')
                    if container_id and previous_states.get(container_id) == 'running':
                        yield f"event: metrics_updated\n"
                        metrics_data = json.dumps({
                            'projectId': container_id,
                            'metrics': {
                                'cpu': random.randint(5, 95),
                                'memory': random.randint(50, 512),
                                'requests': random.randint(0, 1000),
                                'uptime': f"{random.randint(0, 24)}h {random.randint(0, 59)}m",
                                'lastActivity': datetime.utcnow().isoformat() + 'Z'
                            }
                        })
                        yield f"data: {metrics_data}\n\n"
                
                # Simular eventos especiales ocasionalmente
                if random.random() < 0.1:  # 10% de probabilidad
                    container = random.choice(real_containers)
                    container_id = container.get('id')
                    
                    if random.random() < 0.5:
                        # Auto shutdown
                        yield f"event: auto_shutdown\n"
                        shutdown_data = json.dumps({
                            'projectId': container_id,
                            'reason': 'inactivity',
                            'timestamp': datetime.utcnow().isoformat() + 'Z'
                        })
                        yield f"data: {shutdown_data}\n\n"
                        previous_states[container_id] = 'inactive'
                    else:
                        # Error de contenedor
                        yield f"event: container_error\n"
                        container_error_data = json.dumps({
                            'projectId': container_id,
                            'message': 'Container health check failed',
                            'error_code': 'HEALTH_CHECK_FAILED',
                            'timestamp': datetime.utcnow().isoformat() + 'Z'
                        })
                        yield f"data: {container_error_data}\n\n"
                        previous_states[container_id] = 'error'
                
                # Esperar 4 segundos entre ciclos de verificación
                time.sleep(6)
                
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

@sse_bp.route('/containers/events', methods=['OPTIONS'])
def sse_options():
    """Handle preflight requests"""
    return '', 200, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Credentials': 'true'
    }