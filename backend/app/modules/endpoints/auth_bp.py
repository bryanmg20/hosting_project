from flask import Blueprint, request,jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.modules.auth.services.core_service import AuthCoreService
from app.modules.auth.services.validator_service import AuthValidatorService
from app.modules.auth.services.response_service import AuthResponseService
from app.modules.auth.services.login_service import login_service
from app.modules.auth.services.user_service import user_service

# Crear Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Inicializar servicios
auth_core = AuthCoreService(login_service, user_service)
validator = AuthValidatorService()
response_handler = AuthResponseService()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # Validar datos
        validation = validator.validate_registration_data(request.get_json())
        if not validation['valid']:
            return response_handler.error(validation['error'])
        
        # Procesar registro
        result = auth_core.process_registration(
            validation['email'], 
            validation['password'], 
            validation['name']
        )
        
        if not result['success']:
            return response_handler.error(result.get('error', 'Registration failed'))
        
        return response_handler.auth_success(
            result['user_data'],
            result['access_token'],
            result['refresh_token'],
            201
        )
        
    except Exception as e:
        return response_handler.error('Internal server error', 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # Validar datos
        validation = validator.validate_login_data(request.get_json())
        if not validation['valid']:
            return response_handler.error(validation['error'])
        
        # Procesar login
        result = auth_core.process_login(validation['email'], validation['password'])
        
        if not result['success']:
            return response_handler.error('Invalid email or password', 401)
        
        return response_handler.auth_success(
            result['user_data'],
            result['access_token'],
            result['refresh_token']
        )
        
    except Exception as e:
        return response_handler.error('Internal server error', 500)

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_email = get_jwt_identity()
        claims = get_jwt()
        
        user_data = auth_core._get_user_data(user_email)
        user_data['name'] = claims.get('name', user_data['name'])
        
        return response_handler.user_info(user_data)
        
    except Exception as e:
        return response_handler.error('Internal server error', 500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        user_email = get_jwt_identity()
        user_service.clear_user_tokens(user_email)
        return jsonify({'message': 'Successfully logged out'}), 200
    except Exception as e:
        return response_handler.error('Internal server error', 500)