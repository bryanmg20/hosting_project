from .base import BaseAuthService
import time

class UserService(BaseAuthService):
    def get_user_data_with_retry(self, email: str, max_retries: int = 2) -> dict:
        """
        Obtiene los datos del usuario desde la base de datos usando un token válido.
        Si el token expira o hay error temporal, intenta nuevamente hasta max_retries veces.
        """
        try:
            attempt = 0
            while attempt < max_retries:
                attempt += 1

                # 1️⃣ Obtener un token válido
                token_result = self.get_valid_access_token(email)
                if not token_result.get('success'):
                    return {
                        'success': False,
                        'error': 'Failed to obtain valid access token',
                        'details': token_result.get('error')
                    }

                access_token = token_result.get('access_token')
                refresh_token = token_result.get('refresh_token')

                # 2️⃣ Hacer la petición centralizada con _request()
                url = f"{self.database_url}/read?tableName=users&email={email}"
                headers = {'Authorization': f'Bearer {access_token}'}

                response = self._request('GET', url, headers=headers)

                # 3️⃣ Si fue exitosa la petición
                if response.get('success'):
                    return {'success': True, 'data': {'rows': response.get('data')}}

                # 4️⃣ Si fue error de autenticación (token expirado), intenta refrescar
                status_code = response.get('status_code', 0)
                if status_code == 401 and attempt < max_retries:
                    self.refresh_token(refresh_token)
                    continue

                # 5️⃣ Si fue otro tipo de error
                return {
                    'success': False,
                    'error': f"Failed to fetch user data (status {status_code})",
                    'details': response.get('details')
                }

            # 6️⃣ Si se agotaron los intentos
            return {'success': False, 'error': 'Max retries exceeded'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    
    def create_user_in_table(self, access_token: str, user_data: dict) -> dict:
        """Crear usuario en la tabla users de Roble usando el token proporcionado"""
        try:
            url = f"{self.database_url}/insert"
            headers = {'Authorization': f'Bearer {access_token}'}

            payload = {
                'tableName': 'users',
                'records': [user_data]
            }

            # Usar el _request que ya existe
            response = self._request('POST', url, headers=headers, json=payload)

            if response.get('success'):
                return {
                    'success': True,
                    'data': response.get('data')
                }

            return {
                'success': False,
                'error': f"Failed to create user (status {response.get('status_code')})",
                'details': response.get('details')
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    
    def store_roble_tokens(self, email: str, access_token: str, refresh_token: str) -> dict:
        """Almacena los tokens de Roble para el usuario en memoria."""
        try:
            if not hasattr(self, 'tokens_store'):
                self.tokens_store = {}

            self.tokens_store[email] = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'last_updated': time.time()
            }

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_roble_tokens(self, email: str) -> dict:
        """Obtiene los tokens almacenados para un usuario."""
        try:
            tokens = getattr(self, 'tokens_store', {}).get(email)
            
            if tokens:
                return {'success': True, 'data': tokens}
            else:
                return {'success': False, 'error': 'No tokens found for this user'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def clear_user_tokens(self, email: str) -> dict:
        """Elimina los tokens almacenados para un usuario."""
        try:
            if email in self.tokens_store:
                del self.tokens_store[email]
                return {'success': True, 'message': f'Tokens cleared for {email}'}
            else:
                return {'success': False, 'error': 'No tokens found for this user'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

user_service = UserService() 