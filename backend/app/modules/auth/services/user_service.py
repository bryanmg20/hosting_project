from .base import BaseAuthService
from .base import _tokens_store
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
                
                url = f"{self.database_url}/read?tableName=projects&email={email}"
                headers = {'Authorization': f'Bearer {access_token}'}
        
                response = self._request('GET', url, headers=headers)
                
                # CORRECCIÓN: response es una lista directa, no dict con 'success'
                if isinstance(response, list):
                    return {'success': True, 'data': response}  # ← Lista directa
                
                # Si response es dict pero tiene error
                if isinstance(response, dict) and response.get('success'):
                    return {'success': True, 'data': response.get('data', [])}
                
                # 4️⃣ Si fue error de autenticación (token expirado), intenta refrescar
                status_code = response.get('status_code', 0) if isinstance(response, dict) else 0
                if status_code == 401 and attempt < max_retries:
                    self.refresh_token(refresh_token)
                    continue

                # 5️⃣ Si fue otro tipo de error
                return {
                    'success': False,
                    'error': f"Failed to fetch user data (status {status_code})",
                    'details': response.get('details') if isinstance(response, dict) else str(response)
                }

            # 6️⃣ Si se agotaron los intentos
            return {'success': False, 'error': 'Max retries exceeded'}

        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    
    def store_roble_tokens(self, email: str, access_token: str, refresh_token: str) -> dict:
        """Almacena los tokens de Roble para el usuario en memoria."""
        try:
            # Usar directamente el almacenamiento de clase
            _tokens_store[email] = {
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
            # Acceder directamente al almacenamiento de clase
            tokens = _tokens_store.get(email)
            
            if tokens:
                return {'success': True, 'data': tokens}
            else:
                return {'success': False, 'error': 'No tokens found for this user'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def clear_user_tokens(self, email: str) -> dict:
        """Elimina los tokens almacenados para un usuario."""
        try:
            # Acceder directamente al almacenamiento de clase
            if email in _tokens_store:
                del _tokens_store[email]
                return {'success': True, 'message': f'Tokens cleared for {email}'}
            else:
                return {'success': False, 'error': 'No tokens found for this user'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        

    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh token de Roble"""
        try:
            url = f"{self.auth_url}/{self.db_name}/refresh-token"

            # Usamos el método genérico de la base
            data = self._request("POST", url, json={
                'refreshToken': refresh_token
            })

            # Si _request() no lanza excepción, fue éxito
            return {
                'success': True,
                'access_token': data.get('accessToken')
            }

        except Exception as e:
            # Captura cualquier error (HTTP o de red)
            return {
                'success': False,
                'error': str(e)
            }
        
    def verify_token(self, token: str) -> dict:
        """Verifica si el token de Roble es válido."""
        try:
            url = f"{self.auth_url}/verify-token"
            headers = {'Authorization': f'Bearer {token}'}
            
          
            response = self._request('GET', url, headers=headers)
            
            # Si la respuesta fue exitosa
            if response.get('success'):
                return {'success': True, 'valid': True, 'data': response.get('data')}
            
            # Si no fue exitosa
            return {
                'success': False,
                'valid': False,
                'error': 'Invalid token',
                'status_code': response.get('status_code'),
                'details': response.get('details')
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    
    def get_valid_access_token(self, email: str) -> dict:
        """
        Obtiene un access token válido para el usuario.
        Si el token actual expiró, hace refresh automáticamente.
        """
        try:
            # 1. Obtener los tokens almacenados del usuario
            user_tokens_result = self.get_roble_tokens(email)  # ← Cambiar nombre para claridad
            
            # 2. Verificar si la operación fue exitosa
            if not user_tokens_result.get('success'):
                return user_tokens_result  # ← Devolver el error original
            
            # 3. Extraer los tokens del campo 'data'
            user_tokens = user_tokens_result.get('data', {})
            access_token = user_tokens.get('access_token')
            refresh_token = user_tokens.get('refresh_token')

            if not access_token or not refresh_token:
                return {'success': False, 'error': 'No tokens available'}

            # 4. Verificar si el token actual es válido
            verify_result = self.verify_token(access_token)

            if verify_result.get('success') and verify_result.get('valid'):
                return {'success': True, 'access_token': access_token}

            # 5. Si no es válido, intentar refrescar el token
            refresh_result = self.refresh_token(refresh_token)

            if refresh_result.get('success'):
                new_access_token = refresh_result.get('access_token')

                # Guardar los nuevos tokens
                self.store_roble_tokens(email, new_access_token, refresh_token)

                return {'success': True, 'access_token': new_access_token}
            else:
                return {
                    'success': False,
                    'error': 'Token refresh failed',
                    'details': refresh_result.get('error')
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}


user_service = UserService() 