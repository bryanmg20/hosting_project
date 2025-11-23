from flask_jwt_extended import create_access_token, create_refresh_token
import json

class AuthCoreService:
    def __init__(self, login_service, user_service):
        self.login_service = login_service
        self.user_service = user_service
    
    def process_registration(self, email, password, name):
        """Procesa el registro completo del usuario"""
        # 1. Registrar en Roble Auth
        signup_result = self.login_service.signup_direct(email, password, name)
        if not signup_result['success']:
            return signup_result
        
        # 2. Login para obtener tokens
        login_result = self.login_service.login(email, password)
        if not login_result['success']:
            return {'success': False, 'error': 'Registration successful but login failed'}
        
        roble_access_token = login_result['access_token']
        roble_refresh_token = login_result['refresh_token']
        
        # 3. Almacenar tokens
        self.user_service.store_roble_tokens(email, roble_access_token, roble_refresh_token)
        
        # 4. Crear usuario en tabla
        #user_table_data = {'user': name, 'email': email, 'containers': []}
        #self.user_service.create_user_in_table(roble_access_token, user_table_data)
        
        # 5. Generar JWT tokens
        additional_claims = {'name': name, 'email': email}
        access_token = create_access_token(identity=email, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=email, additional_claims=additional_claims)
        
        return {
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_data': {'email': email, 'name': name, 'containers': []}
        }
    
    def process_login(self, email, password):
        """Procesa el login completo del usuario"""
        # 1. Login con Roble Auth
        login_result = self.login_service.login(email, password)
        if not login_result['success']:
            return login_result
        
        roble_access_token = login_result['access_token']
        roble_refresh_token = login_result['refresh_token']
        
        # 2. Almacenar tokens
        self.user_service.store_roble_tokens(email, roble_access_token, roble_refresh_token)
        
        # 3. Obtener datos del usuario
        user_data = self._get_user_data(email)
        
        # 4. Generar JWT tokens
        additional_claims = {'name': user_data['name'], 'email': email}
        access_token = create_access_token(identity=email, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=email, additional_claims=additional_claims)
        
        
        return {
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_data': user_data
        }
    
    def _get_user_data(self, email):
        """Obtiene datos del usuario de Roble"""
        user_data_result = self.user_service.get_user_data_with_retry(email)
        username = 'not_found'
        if user_data_result['success']:
            username = user_data_result['data'][0].get('username','not_found')  # ← Sin .get('rows')
               
        return {'email': email, 'name': username}