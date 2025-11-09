from .base import BaseAuthService

class TokenService(BaseAuthService):
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
            # Obtener los tokens almacenados del usuario
            user_tokens = self.get_roble_tokens(email)
            access_token = user_tokens.get('access_token')
            refresh_token = user_tokens.get('refresh_token')

            if not access_token or not refresh_token:
                return {'success': False, 'error': 'No tokens available'}

            # Verificar si el token actual es válido
            verify_result = self.verify_token(access_token)

            if verify_result.get('success') and verify_result.get('valid'):
                return {'success': True, 'access_token': access_token}

            # Si no es válido, intentar refrescar el token
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

token_service = TokenService()