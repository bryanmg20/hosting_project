from .base import BaseAuthService
import json

class LoginService(BaseAuthService):
    def login(self, email: str, password: str) -> dict:
        """Login con Roble Auth"""
        try:
            url = f"{self.auth_url}/{self.db_name}/login"
            
            # Aquí usamos el método genérico _request de la clase base
            response = self._request("POST", url, json={
                'email': email,
                'password': password
            })

            # Si la API responde correctamente, formateamos la salida
            return {
                'success': True,
                'access_token': response.get('accessToken'),
                'refresh_token': response.get('refreshToken')
            }

        except Exception as e:
            # Si la API devuelve error o raise_for_status() lanza excepción
            return {
                'success': False,
                'error': str(e)
            }

    def signup_direct(self, email: str, password: str, name: str) -> dict:
        """Registro directo sin verificación de email"""
        try:
            url = f"{self.auth_url}/{self.db_name}/signup-direct"
            data = self._request("POST", url, json={
                'email': email,
                'password': password,
                'name': name
            })
            return {
                'success': True,
                'data': data
            }

        except Exception as e:
            # Intentamos obtener el cuerpo del error si está disponible
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except ValueError:
                    error_detail = e.response.text
            if isinstance(error_detail, dict):
                error_detail = json.dumps(error_detail, ensure_ascii=False)

            return {
                'success': False,
                'error': error_detail
            }
    
login_service = LoginService() 