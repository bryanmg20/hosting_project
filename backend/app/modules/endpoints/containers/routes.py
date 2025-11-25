
"""
Rutas Flask para la gestión de contenedores.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .lifecycle import start_container_logic, stop_container_logic
from .builder import create_container_logic
from .rebuilder import rebuild_container_logic

container_bp = Blueprint('container', __name__)


@container_bp.route('/containers/<container_id>/start', methods=['POST'])
@jwt_required()
def start_container(container_id):
    """
    Inicia un contenedor previamente creado.
    """
    response, status = start_container_logic(container_id)
    return jsonify(response), status


@container_bp.route('/containers/<container_id>/stop', methods=['POST'])
@jwt_required()
def stop_container(container_id):
    """
    Detiene un contenedor previamente creado y/o iniciado.
    """
    response, status = stop_container_logic(container_id)
    return jsonify(response), status


@container_bp.route('/containers/<container_id>/rebuild', methods=['POST'])
@jwt_required()
def restart_container(container_id):
    """
    Reconstruye el contenedor del proyecto sin borrar el proyecto.
    """
    payload = request.get_json(silent=True) or {}
    response, status = rebuild_container_logic(container_id, payload)
    return jsonify(response), status


@container_bp.route('/containers/<container_id>/create', methods=['POST'])
@jwt_required()
def create_container(container_id):
    """
    Construye la imagen Docker del proyecto y crea el contenedor.
    """
    payload = request.get_json(silent=True) or {}
    response, status = create_container_logic(container_id, payload)
    return jsonify(response), status
