# app/modules/auth/service.py
import requests
import os
import json
import time

class RobleAuthService:
    def __init__(self, roble_db_name=None):
        self.auth_url = 'https://roble-api.openlab.uninorte.edu.co/auth'
        self.db_name = roble_db_name or os.environ.get('ROBLE_DB_NAME', 'tu_base_datos')
        self.database_url = f"https://roble-api.openlab.uninorte.edu.co/database/{self.db_name}"
        self.tokens_store = {}
    
    def login(self, email: str, password: str) -> dict:
        """Login con Roble Auth"""
        try:
            url = f"{self.auth_url}/{self.db_name}/login"
            response = requests.post(url, json={
                'email': email,
                'password': password
            })
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                return {
                    'success': True, 
                    'access_token': data.get('accessToken'),
                    'refresh_token': data.get('refreshToken')
                }
            else:
                return {
                    'success': False, 
                    'error': 'Invalid email or password',
                    'status_code': response.status_code
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh token de Roble"""
        try:
            url = f"{self.auth_url}/{self.db_name}/refresh-token"
            response = requests.post(url, json={
                'refreshToken': refresh_token
            })
            
            if response.status_code == 201:
                data = response.json()
                return {
                    'success': True,
                    'access_token': data.get('accessToken')
                }
            else:
                return {
                    'success': False,
                    'error': 'Refresh token failed',
                    'status_code': response.status_code
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def signup_direct(self, email: str, password: str, name: str) -> dict:
        """Registro directo sin verificación de email"""
        try:
            url = f"{self.auth_url}/{self.db_name}/signup-direct"
            print(f"🔗 URL de Roble: {url}")
            
            response = requests.post(url, json={
                'email': email,
                'password': password,
                'name': name
            })
            
            print(f"📡 Response Status: {response.status_code}")
            print(f"📡 Response Text: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                return {'success': True, 'data': response.json()}
            else:
                # Incluir el response.text en el error para ver el mensaje real de Roble
                return {
                    'success': False, 
                    'error': 'Registration failed',
                    'status_code': response.status_code,
                    'details': response.text  # ← Esto tiene el error específico
                }
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_token(self, token: str) -> dict:
        """Verificar si el token de Roble es válido"""
        try:
            url = f"{self.auth_url}/{self.db_name}/verify-token"
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(url, headers=headers)
            
            return {
                'success': response.status_code == 201,
                'valid': response.status_code == 201
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_data_with_retry(self, email: str, max_retries: int = 2) -> dict:
        """Obtener datos del usuario con reintentos si el token expira"""
        user_tokens = self.tokens_store.get(email, {})
        access_token = user_tokens.get('access_token')
        refresh_token = user_tokens.get('refresh_token')
        
        if not access_token:
            return {'success': False, 'error': 'No tokens available'}
        
        for attempt in range(max_retries):
            try:
                verify_result = self.verify_token(access_token)
                
                if not verify_result['valid'] and attempt == 0 and refresh_token:
                    refresh_result = self.refresh_token(refresh_token)
                    if refresh_result['success']:
                        access_token = refresh_result['access_token']
                        self.tokens_store[email] = {
                            'access_token': access_token,
                            'refresh_token': refresh_token
                        }
                    else:
                        return {'success': False, 'error': 'Token refresh failed'}
                
                url = f"{self.database_url}/table-data?table=users"
                headers = {'Authorization': f'Bearer {access_token}'}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 201:
                    return {'success': True, 'data': response.json()}
                elif response.status_code == 401 and attempt == 0 and refresh_token:
                    continue
                else:
                    return {
                        'success': False, 
                        'error': f'Failed to fetch user data: {response.status_code}'
                    }
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Max retries exceeded'}
    
    def create_user_in_table(self, access_token: str, user_data: dict) -> dict:
        """Crear usuario en la tabla users de Roble"""
        try:
            url = f"{self.database_url}/insert"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.post(url, headers=headers, json={
                'tableName': 'users',
                'records': [user_data]  # ← 'records' en array, no 'data'
            })
            
            print(f"🔗 Insert URL: {url}")
            print(f"📡 Insert Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json()}
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'details': response.text
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def store_roble_tokens(self, email: str, access_token: str, refresh_token: str):
        """Almacenar tokens de Roble para el usuario"""
        self.tokens_store[email] = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'last_updated': time.time()
        }
    
    def get_roble_tokens(self, email: str) -> dict:
        """Obtener tokens de Roble almacenados"""
        return self.tokens_store.get(email, {})
    
    def clear_user_tokens(self, email: str):
        """Limpiar tokens de un usuario"""
        if email in self.tokens_store:
            del self.tokens_store[email]

# Instancia global del servicio
roble_auth = RobleAuthService()