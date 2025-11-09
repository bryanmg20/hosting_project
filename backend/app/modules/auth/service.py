# app/modules/auth/service.py
import requests
import os
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
        
            
            response = requests.post(url, json={
                'email': email,
                'password': password,
                'name': name
            })
            
            
            if response.status_code == 200 or response.status_code == 201:
                return {'success': True, 'data': response.json()}
            else:
                return {
                    'success': False, 
                    'error': 'Registration failed',
                    'status_code': response.status_code,
                    'details': response.text
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_token(self, token: str) -> dict:
        """Verificar si el token de Roble es válido"""
        try:
            url = f"{self.auth_url}/{self.db_name}/verify-token"
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(url, headers=headers)
            
            return {
                'success': response.status_code == 200,
                'valid': response.status_code == 200
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_valid_access_token(self, email: str) -> dict:
        """
        Obtener un access token válido para el usuario.
        Si el token actual expiró, hace refresh automáticamente.
        """
        try:
            
            user_tokens = self.get_roble_tokens(email)
            access_token = user_tokens.get('access_token')
            refresh_token = user_tokens.get('refresh_token')
            
            if not access_token or not refresh_token:
                
                return {'success': False, 'error': 'No tokens available'}
            
            # Verificar si el token actual es válido
            verify_result = self.verify_token(access_token)
            
            if verify_result.get('valid'):
                
                return {'success': True, 'access_token': access_token}
            
            # Si no es válido, hacer refresh
           
            refresh_result = self.refresh_token(refresh_token)
    
            
            if refresh_result['success']:
                new_access_token = refresh_result['access_token']
                # Actualizar en el storage


                self.store_roble_tokens(email, new_access_token, refresh_token)
               
                return {'success': True, 'access_token': new_access_token}
            else:
               
                return {'success': False, 'error': 'Token refresh failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_data_with_retry(self, email: str, max_retries: int = 2) -> dict:
        """Obtener datos del usuario usando token válido"""
        try:
            # Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result
            
            access_token = token_result['access_token']
            
            # Hacer la request
            url = f"{self.database_url}/read?tableName=users&email={email}"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 or  response.status_code == 201:
                data = response.json()
                return {'success': True, 'data': {'rows': data}}
            else:
                return {
                    'success': False, 
                    'error': f'Failed to fetch user data: {response.status_code}',
                    'response_text': response.text
                }
                        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_user_in_table(self, email: str, user_data: dict) -> dict:
        """Crear usuario en la tabla users de Roble"""
        try:
            # Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result
            
            access_token = token_result['access_token']
            
            url = f"{self.database_url}/insert"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.post(url, headers=headers, json={
                'tableName': 'users',
                'records': [user_data]
            })
            
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
    
    def get_user_containers(self, email: str) -> dict:
        """Obtener todos los contenedores de un usuario"""
        try:
            import json
            
            # Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result
            
            access_token = token_result['access_token']
            
            # Hacer la request
            url = f"{self.database_url}/read?tableName=users&email={email}"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                if user_data and len(user_data) > 0:
                    containers_data = user_data[0].get('containers', '[]')
                    
                    # Manejar JSON string
                    if isinstance(containers_data, str):
                        try:
                            containers = json.loads(containers_data)
                        except json.JSONDecodeError:
                            containers = []
                    else:
                        containers = containers_data
                    
                    # Normalizar a lista
                    if isinstance(containers, dict):
                        containers = list(containers.values())
                    elif not isinstance(containers, list):
                        containers = []
                    
                    return {'success': True, 'containers': containers}
                else:
                    return {'success': True, 'containers': []}
            else:
                return {'success': False, 'error': f'Failed to fetch containers: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_container_to_user(self, email: str, project_id: str, name: str, url: str, template: str, github_url: str, created: str) -> dict:
        """Agregar un contenedor a la columna containers del usuario"""
        try:
            import json
            
            # Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result
            
            access_token = token_result['access_token']
            
            # 1. Crear nuevo contenedor
            new_container = {
                'id': project_id,
                'name': name,
                'url': url,
                'template': template,
                'github_url': github_url,
                'created_at': created
            }
            
            # 2. Obtener containers existentes
            containers_result = self.get_user_containers(email)
            if not containers_result['success']:
                return containers_result
            
            existing_containers = containers_result['containers']
            existing_containers.append(new_container)
            containers_json = json.dumps(existing_containers)
            
            # 3. Hacer el update
            update_url = f"{self.database_url}/update"
            headers = {'Authorization': f'Bearer {access_token}'}
            update_data = {
                'tableName': 'users',
                'idColumn': 'email',
                'idValue': email,
                'updates': {'containers': containers_json}
            }
            
            response = requests.put(update_url, headers=headers, json=update_data)
            
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json(), 'container': new_container}
            else:
                return {
                    'success': False,
                    'error': f'Failed to update containers: {response.status_code}',
                    'details': response.text
                }
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_container_by_id(self, email: str, project_id: str) -> dict:
        """Obtener un contenedor específico por project_id"""
        try:
            containers_result = self.get_user_containers(email)
            if not containers_result['success']:
                return containers_result
            
            containers = containers_result['containers']
            container = next((c for c in containers if c['id'] == project_id), None)
            
            if container:
                return {'success': True, 'container': container}
            else:
                return {'success': False, 'error': 'Container not found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Instancia global del servicio
roble_auth = RobleAuthService()