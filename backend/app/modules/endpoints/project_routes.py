from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.modules.auth.services.project_service import project_service
from app.modules.project.validators import validate_create_project_data
from app.modules.project.project_logic import format_project_list, format_project_response, create_new_project_data
from app.modules.project.responses import success_response, list_response, error_response

project_bp = Blueprint('project', __name__)

@project_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """
    Obtener todos los proyectos del usuario autenticado
    """
    try:

        # 1. Obtener usuario autenticado
        user_email = get_jwt_identity()
        
        if not user_email:
            return error_response('User not authenticated', 401)
        
        # 2. Obtener contenedores del usuario
        containers_result = project_service.get_user_projects(user_email)
        
        if not containers_result['success']:
            return error_response(
                f'Failed to fetch projects: {containers_result.get("error")}', 
                500
            )
        
        # 3. Procesar y formatear proyectos
        containers = containers_result.get('projects', [])
        projects = format_project_list(containers)
        
        # 4. Retornar respuesta
        return list_response(projects)
        
    except Exception as e:
        return error_response('Internal server error', 500)
    
@project_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():


    try:
        # Validar datos
        validation = validate_create_project_data(request.get_json())
        if not validation['valid']:
            return error_response(validation['error'])
        
        user_email = get_jwt_identity()
        claims = get_jwt()
        username = claims.get('name', 'Usuario')


        
        if not user_email:
            return error_response('User not authenticated', 401)
        
        # Crear proyecto en Roble
        project_data = create_new_project_data(
            validation['name'], 
            username,  
            validation['github_url']
        )
    
        
        result = project_service.create_project(
        email=user_email,
        project_name=project_data['name'],
        url=project_data['url'],
        github_url=project_data['github_url'],
        created_time=project_data['created_at']
     )
      
    

        
        if not result['success']:
            return error_response(f'Failed to create project: {result.get("error")}', 500)
        
        return success_response(project_data, 'Project created successfully', 201)
        
    except Exception as e:
        return error_response('Internal server error', 500)

@project_bp.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    try:
        user_email = get_jwt_identity()
        result = project_service.get_project_by_id(user_email, project_id)
        
        if not result['success']:
            return error_response(result.get('error', 'Project not found'), 404)
        
        project_response = format_project_response(result['project'])
        return success_response(project_response)
        
    except Exception as e:
        return error_response('Internal server error', 500)

# Los endpoints DELETE y PATCH los mantienes similares

@project_bp.route('/projects/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """
    Eliminar un proyecto específico del usuario
    """
    try:
        user_email = get_jwt_identity()
        
        if not user_email:
            return error_response('User not authenticated', 401)
        
        #aqui se tiene que eliminar el contenedor antes que el proyecto

        project_result = project_service.delete_project(user_email, project_id)

        if not project_result['success']:
            return error_response('Project not found', 404)
        
        return success_response(None, 'Project deleted successfully', 200)
        
    except Exception as e:
        return error_response('Internal server error', 500)
