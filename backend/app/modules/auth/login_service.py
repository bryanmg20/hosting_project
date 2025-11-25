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
                    json_error = e.response.json()

                    # Si el JSON tiene "message", procesamos solo ese caso
                    if isinstance(json_error, dict) and "message" in json_error:
                        backend_msg = json_error["message"]

                        # Caso específico: correo ya registrado
                        if backend_msg == "El correo ya está registrado":
                            error_detail = "Email is already registered"
                        else:
                            error_detail = backend_msg

                    else:
                        error_detail = json_error

                except ValueError:
                    error_detail = e.response.text
                    
            if isinstance(error_detail, dict):
                error_detail = json.dumps(error_detail, ensure_ascii=False)

            return {
                'success': False,
                'error': error_detail
            }
    
login_service = LoginService() 