from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

container_bp = Blueprint('container', __name__)

@container_bp.route('/containers/<container_id>/start', methods=['POST'])
@jwt_required()
def start_container(container_id):
    """Mock para iniciar contenedor"""
    # apiClient SIEMPRE espera JSON, incluso para POST vacíos
    return jsonify({
        'success': True,
        'message': f'Container {container_id} started successfully'
    }), 200

@container_bp.route('/containers/<container_id>/stop', methods=['POST'])
@jwt_required()
def stop_container(container_id):
    """Mock para detener contenedor"""
    return jsonify({
        'success': True,
        'message': f'Container {container_id} stopped successfully'
    }), 200

@container_bp.route('/containers/<container_id>/rebuild', methods=['POST'])
@jwt_required()
def restart_container(container_id):
    """Mock para reiniciar contenedor"""
    return jsonify({
        'success': True,
        'message': f'Container {container_id} restarted successfully'
    }), 200

@container_bp.route('/containers/<container_id>/create', methods=['POST'])
@jwt_required()
def create_container(container_id):
 
    """Mock para reiniciar contenedor"""
    return jsonify({
        'success': True,
        'message': f'Container {container_id} created successfully'
    }), 200
