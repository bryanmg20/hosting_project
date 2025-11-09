# app/modules/auth/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import json

from app.modules.auth.service import roble_auth

# Crear Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Utilidad para validar email
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========================================
# POST /api/auth/register
# ========================================
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        name = data['name'].strip()
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        # 1. Registrar usuario en Roble Auth
        signup_result = roble_auth.signup_direct(email, password, name)
        
        if not signup_result['success']:
            error_msg = signup_result.get('error', 'Registration failed')
            return jsonify({'error': error_msg}), 400
        
        # 2. Hacer login para obtener tokens de Roble
        login_result = roble_auth.login(email, password)
        
        if not login_result['success']:
            return jsonify({'error': 'Registration successful but login failed'}), 400
        
        roble_access_token = login_result['access_token']
        roble_refresh_token = login_result['refresh_token']
        
        # 3. Almacenar tokens de Roble
        roble_auth.store_roble_tokens(email, roble_access_token, roble_refresh_token)
        
        # 4. Crear usuario en tabla users
        user_table_data = {
            'user': name,
            'email': email,
            'containers': [],
        }
        
        table_result = roble_auth.create_user_in_table(roble_access_token, user_table_data)
        
        if not table_result['success']:
            # Continuamos aunque falle la creación en la tabla
            pass
        
        # 5. Generar tokens JWT
        additional_claims = {'name': name, 'email': email}
        access_token = create_access_token(identity=email, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=email, additional_claims=additional_claims)
        
        user_response = {
            'id': email,
            'email': email,
            'name': name,
            'containers': []
        }
        
        return jsonify({
            'user': user_response,
            'token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
# ========================================
# POST /api/auth/login
# ========================================
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # 1. Login con Roble Auth
        login_result = roble_auth.login(email, password)
        
        if not login_result['success']:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        roble_access_token = login_result['access_token']
        roble_refresh_token = login_result['refresh_token']
        
        # 2. Almacenar tokens de Roble
        roble_auth.store_roble_tokens(email, roble_access_token, roble_refresh_token)
        
        # 3. Obtener datos del usuario con manejo de token expirado
        user_data_result = roble_auth.get_user_data_with_retry(email)
       
        
        user_name = "Usuario"
        containers = []
        
        if user_data_result['success']:
            for user_row in user_data_result['data'].get('rows', []):
                if user_row.get('email') == email:
                    user_name = user_row.get('user', user_row.get('name', 'Usuario'))
                    containers_str = user_row.get('containers', '[]')
                    try:
                        containers = json.loads(containers_str)
                    except:
                        containers = []
                    break
        
        # 4. Generar tokens JWT
        additional_claims = {'name': user_name, 'email': email}
        access_token = create_access_token(identity=email, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=email, additional_claims=additional_claims)
        
        user_response = {
            'id': email,
            'email': email,
            'name': user_name,
            'containers': containers
        }
        
        return jsonify({
            'user': user_response,
            'token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# ========================================
# GET /api/auth/me
# ========================================
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_email = get_jwt_identity()
        claims = get_jwt()
        
        user_name = claims.get('name', 'Usuario')
        containers = []
        
        # Obtener datos actualizados de Roble con manejo de token
        user_data_result = roble_auth.get_user_data_with_retry(user_email)
        
        if user_data_result['success']:
            for user_row in user_data_result['data'].get('rows', []):
                if user_row.get('email') == user_email:
                    containers_str = user_row.get('containers', '[]')
                    try:
                        containers = json.loads(containers_str)
                    except:
                        containers = []
                    break
        
        user_response = {
            'id': user_email,
            'email': user_email,
            'name': user_name,
            'containers': containers
        }
        
        return jsonify({'user': user_response}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# ========================================
# POST /api/auth/logout
# ========================================
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        user_email = get_jwt_identity()
        
        # Limpiar tokens de Roble almacenados
        roble_auth.clear_user_tokens(user_email)
        
        return jsonify({'message': 'Successfully logged out'}), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
    

