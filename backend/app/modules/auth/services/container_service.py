from .base import BaseAuthService

class ContainerService(BaseAuthService):
    def get_user_containers(self, email: str) -> dict:
        """Obtener todos los contenedores de un usuario"""
        try:
            import json
            
            # Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result
            
            access_token = token_result['access_token']

            # Usar el método genérico _request
            url = f"{self.database_url}/read?tableName=users&email={email}"
            response = self._request('GET', url, headers={'Authorization': f'Bearer {access_token}'})

            if response['success']:
                user_data = response['data']
                if user_data and len(user_data) > 0:
                    containers_data = user_data[0].get('containers', '[]')

                    if isinstance(containers_data, str):
                        try:
                            containers = json.loads(containers_data)
                        except json.JSONDecodeError:
                            containers = []
                    else:
                        containers = containers_data

                    if isinstance(containers, dict):
                        containers = list(containers.values())
                    elif not isinstance(containers, list):
                        containers = []

                    return {'success': True, 'containers': containers}
                else:
                    return {'success': True, 'containers': []}
            else:
                return {'success': False, 'error': response.get('error', 'Unknown error')}

        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_container_to_user(
    self,
    email: str,
    project_id: str,
    name: str,
    url: str,
    template: str,
    github_url: str,
    created: str
) -> dict:
        """Agregar un contenedor a la columna containers del usuario"""
        try:
            import json

            # 1. Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result

            access_token = token_result['access_token']

            # 2. Crear nuevo contenedor
            new_container = {
                'id': project_id,
                'name': name,
                'url': url,
                'template': template,
                'github_url': github_url,
                'created_at': created
            }

            # 3. Obtener containers existentes
            containers_result = self.get_user_containers(email)
            if not containers_result['success']:
                return containers_result

            existing_containers = containers_result['containers']
            existing_containers.append(new_container)

            # 4. Preparar actualización
            update_url = f"{self.database_url}/update"
            headers = {'Authorization': f'Bearer {access_token}'}
            update_data = {
                'tableName': 'users',
                'idColumn': 'email',
                'idValue': email,
                'updates': {'containers': json.dumps(existing_containers)}
            }

            # 5. Usar el método genérico _request
            response = self._request('PUT', update_url, headers=headers, json=update_data)

            if response['success']:
                return {'success': True, 'data': response['data'], 'container': new_container}
            else:
                return {'success': False, 'error': response.get('error', 'Failed to update containers')}

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

