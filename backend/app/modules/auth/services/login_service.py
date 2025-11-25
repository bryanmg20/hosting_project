from .base import BaseAuthService

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
            print(url, flush=True)
            # Petición genérica usando la función base
            data = self._request("POST", url, json={
                'email': email,
                'password': password,
                'name': name
            })
            print("data:")
            print(data, flush=True)

            # Si no lanza excepción, es éxito
            return {
                'success': True,
                'data': data
            }

        except Exception as e:
            # Captura cualquier error o código no 2xx
            print("error", flush=True)
            return {
                'success': False,
                'error': str(e)
            }
    
login_service = LoginService() 