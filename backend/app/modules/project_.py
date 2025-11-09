from flask import Flask, request, jsonify, Blueprint
from datetime import datetime
import uuid
from app.modules.auth.service import roble_auth
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

project = Blueprint('project',  __name__)

# Mock database
projects_db = []

# ========================================
# GET /api/projects
# ========================================
@project.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """
    Obtener todos los proyectos del usuario autenticado
    """
    try:
        from flask import current_app
        current_app.logger.info("🎯 GET /projects - Getting all projects")
        
        # Obtener email del usuario autenticado
        user_email = get_jwt_identity()
        current_app.logger.info(f"🔐 Authenticated user: {user_email}")
        
        if not user_email:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Obtener todos los contenedores del usuario desde Roble
        containers_result = roble_auth.get_user_containers(user_email)
        
        if not containers_result['success']:
            current_app.logger.error(f"❌ Failed to fetch projects: {containers_result.get('error')}")
            return jsonify({
                'error': f'Failed to fetch projects: {containers_result.get("error", "Unknown error")}'
            }), 500
        
        containers = containers_result['containers']
        current_app.logger.info(f"📦 Found {len(containers)} containers from Roble")
        
        # Convertir contenedores a estructura de proyecto según Figma
        projects = []
        for container in containers:
            project_data = {
                'id': container.get('id'),
                'name': container.get('name'),
                'status': 'stopped',  # Puedes hacer esto dinámico basado en estado real
                'url': container.get('url'),
                'template': container.get('template'),
                'github_url': container.get('github_url'),
                'created_at': container.get('created_at'),
                'metrics': {
                    'cpu': 0,    # Puedes obtener métricas reales si las tienes
                    'memory': 0,
                    'requests': 0
                }
            }
            projects.append(project_data)
        
        current_app.logger.info(f"✅ Returning {len(projects)} projects")
        
        return jsonify({
            'projects': projects,
            'count': len(projects)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"💥 Error in get_projects: {str(e)}")
        import traceback
        current_app.logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500
# ========================================
# POST /api/projects
# ========================================
@project.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """
    Crear un nuevo proyecto
    """
    try:
        from flask import current_app
        current_app.logger.info("🎯 START /projects endpoint")
        
        data = request.get_json()
        current_app.logger.info(f"📦 Received data: {data}")
        
        if not data:
            current_app.logger.error("❌ No JSON data provided")
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validar campos requeridos
        required_fields = ['name', 'github_url', 'template']
        for field in required_fields:
            if field not in data:
                current_app.logger.error(f"❌ Missing required field: {field}")
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        name = data['name']
        github_url = data['github_url']
        template = data['template']
        
        current_app.logger.info(f"🔧 Validated fields - Name: {name}, Template: {template}, GitHub: {github_url}")
        
        # Validaciones básicas
        if not name or not isinstance(name, str):
            current_app.logger.error("❌ Name validation failed")
            return jsonify({'error': 'Name must be a non-empty string'}), 400
        
        if not github_url or not isinstance(github_url, str):
            current_app.logger.error("❌ GitHub URL validation failed")
            return jsonify({'error': 'GitHub URL must be a non-empty string'}), 400
        
        # Validar template
        valid_templates = ['react', 'static', 'flask']
        if template not in valid_templates:
            current_app.logger.error(f"❌ Invalid template: {template}")
            return jsonify({
                'error': f'Invalid template. Must be one of: {", ".join(valid_templates)}'
            }), 400
        
        user_email = get_jwt_identity()
        claims = get_jwt()
        username = claims.get('name', 'Usuario')

        current_app.logger.info(f"🔐 User authenticated - Email: {user_email}, Username: {username}")

        if not user_email:
            current_app.logger.error("❌ User not authenticated")
            return jsonify({'error': 'User not authenticated'}), 401
    
        if not username:
            current_app.logger.error("❌ Username not found in JWT claims")
            return jsonify({'error': 'Username not found for user'}), 400
    
        # Crear nuevo proyecto con estructura EXACTA de Figma
        project_id = f"proj-{uuid.uuid4().hex[:8]}"
        current_app.logger.info(f"🆕 Generated project ID: {project_id}")
    
        # Formar la URL con el formato: project_name.username.localhost
        project_url = f"{name}.{username}.localhost"
        created = datetime.utcnow().isoformat() + 'Z'
        
        current_app.logger.info(f"🌐 Project URL: {project_url}")
        current_app.logger.info(f"🕐 Created at: {created}")
        
        # Guardar en Roble (con URL en el formato correcto)
        current_app.logger.info("💾 Calling roble_auth.add_container_to_user...")
        result = roble_auth.add_container_to_user(
            email=user_email,
            project_id=project_id,
            name=name,
            url=project_url,
            template=template,
            github_url=github_url,
            created=created
        )
        
        current_app.logger.info(f"📡 Roble result: {result}")
        
        if not result['success']:
            current_app.logger.error(f"❌ Roble failed: {result.get('error', 'Unknown error')}")
            return jsonify({
                'error': f'Failed to create project: {result.get("error", "Unknown error")}'
            }), 500
    
        # Crear objeto de respuesta con estructura EXACTA de Figma
        new_project = {
            'id': project_id,
            'name': name,
            'status': 'deploying', 
            'url': project_url,  # Usar el formato project_name.username.localhost
            'template': template,
            'github_url': github_url,
            'created_at': created,
            'metrics': {  # Métricas según Figma (sin 'resources')
                'cpu': 0,
                'memory': 0,
                'requests': 0
            }
        }
        
        current_app.logger.info("✅ Project created successfully")
        current_app.logger.info(f"📊 Final project object: {new_project}")
    
        # Response EXACTA según Figma
        return jsonify({
            'project': new_project,
            'message': 'Project created successfully'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"💥 UNEXPECTED ERROR in create_project: {str(e)}")
        import traceback
        current_app.logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
# ========================================
# GET /api/projects/:id
# ========================================
@project.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    user_email = get_jwt_identity()
    
    # Usa la función específica que ya existe
    result = roble_auth.get_container_by_id(user_email, project_id)
    
    if not result['success']:
        return jsonify({'error': result.get('error', 'Project not found')}), 404
    
    # Convertir a estructura Figma
    container = result['container']
    project_response = {
        'id': container['id'],
        'name': container['name'],
        'status': 'running',
        'url': container['url'],
        'template': container['template'],
        'github_url': container['github_url'],
        'created_at': container['created_at'],
        'metrics': {'cpu': 0, 'memory': 0, 'requests': 0}
    }
    
    return jsonify({'project': project_response}), 200
# ========================================
# DELETE /api/projects/:id
# ========================================
@project.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    Eliminar un proyecto
    """
    global projects_db
    initial_length = len(projects_db)
    projects_db = [p for p in projects_db if p['id'] != project_id]
    
    if len(projects_db) == initial_length:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify({'message': 'Project deleted successfully'})

# ========================================
# PATCH /api/projects/:id/status
# ========================================
@project.route('/projects/<project_id>/status', methods=['PATCH'])
def update_project_status(project_id):
    """
    Actualizar el estado de un proyecto
    """
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'error': 'Missing status field'}), 400
    
    project = next((p for p in projects_db if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Validar estados según Figma
    valid_statuses = ['deploying', 'stopped', 'running', 'error']
    if data['status'] not in valid_statuses:
        return jsonify({
            'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
        }), 400
    
    # Actualizar estado
    project['status'] = data['status']
    project['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    return jsonify({
        'project': project
    })