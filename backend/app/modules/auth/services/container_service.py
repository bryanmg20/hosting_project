from .user_service import UserService

class ContainerService(UserService):
    def get_user_projects(self, email: str) -> dict:
        """Obtener todos los proyectos de un usuario desde la tabla projects"""
        try:
            # 1. Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result
            
            access_token = token_result['access_token']
            
            # 2. Hacer request a la tabla projects filtrando por email
            url = f"{self.database_url}/read?tableName=projects&email={email}"
            response = self._request('GET', url, headers={'Authorization': f'Bearer {access_token}'})
            
            # 3. Procesar respuesta
            if isinstance(response, list):
                print(f"📊 Proyectos encontrados para {email}: {len(response)}", flush=True)
                return {'success': True, 'projects': response}
            else:
                return {'success': True, 'projects': []}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_project(
        self,
        email: str,
        project_name: str,
        url: str,
        github_url: str,
        created_time:str
    ) -> dict:
        """Crear un nuevo proyecto en la tabla projects"""
        try:
            # 1. Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result

            access_token = token_result['access_token']

            # 3. Crear nuevo proyecto
            new_project = {
                'email': email,
                'project_name': project_name,
                'url': url,
                'github_url': github_url,
                'username': email.split('@')[0],
                'created_at': created_time
            }
            print(f"🆕 Creando proyecto para {email}: {project_name}", flush=True)
            # 4. Insertar en la tabla projects
            insert_url = f"{self.database_url}/insert"
            headers = {'Authorization': f'Bearer {access_token}'}
            insert_data = {
                'tableName': 'projects',
                'records': [new_project]
            }
            print(f"🔗 Insert data: {insert_data}", flush=True)
            # 5. Usar el método genérico _request
            response = self._request('POST', insert_url, headers=headers, json=insert_data)
            
            if isinstance(response, dict) and 'inserted' in response:
                if response['inserted'] and len(response['inserted']) > 0:
                    created_project = response['inserted'][0]
                    print(f"✅ Proyecto creado: {created_project.get('_id')}", flush=True)
                    return {'success': True, 'project': created_project}
                else:
                    # Verificar si hay errores en skipped
                    if response.get('skipped'):
                        error_msg = response['skipped'][0].get('reason', 'Unknown error')
                        return {'success': False, 'error': error_msg}
                    return {'success': False, 'error': 'Failed to create project'}
            else:
                return {'success': False, 'error': 'Invalid response format'}

        except Exception as e:
            print(f"❌ Error creando proyecto: {e}", flush=True)
            return {'success': False, 'error': str(e)}

    def get_project_by_id(self, email: str, project_id: str) -> dict:
        """Obtener un proyecto específico por _id (generado por la BD)"""
        try:
            # 1. Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result
            
            access_token = token_result['access_token']
            
            # 2. Buscar proyecto por _id (generado por Roble) y email (seguridad)
            url = f"{self.database_url}/read?tableName=projects&_id={project_id}&email={email}"
            response = self._request('GET', url, headers={'Authorization': f'Bearer {access_token}'})
            
            if isinstance(response, list) and len(response) > 0:
                project = response[0]
                return {'success': True, 'project': project}
            else:
                return {'success': False, 'error': 'Project not found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_project_by_name(self, email: str, project_name: str) -> dict:
        """Obtener un proyecto específico por project_name"""
        try:
            # 1. Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result
            
            access_token = token_result['access_token']
            
            # 2. Buscar proyecto por project_name y email (doble verificación)
            url = f"{self.database_url}/read?tableName=projects&project_name={project_name}&email={email}"
            response = self._request('GET', url, headers={'Authorization': f'Bearer {access_token}'})
            
            if isinstance(response, list) and len(response) > 0:
                project = response[0]
                return {'success': True, 'project': project}
            else:
                return {'success': False, 'error': 'Project not found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_project(self, email: str, project_id: str) -> dict:
        """Eliminar un proyecto por _id"""
        try:
            # 1. Obtener token válido
            token_result = self.get_valid_access_token(email)
            if not token_result['success']:
                return token_result

            access_token = token_result['access_token']


            # 3. Eliminar proyecto usando _id
            delete_url = f"{self.database_url}/delete"
            headers = {'Authorization': f'Bearer {access_token}'}
            delete_data = {
                'tableName': 'projects',
                'idColumn': '_id',  # Usar _id generado por Roble
                'idValue': project_id
            }
            print(f"🗑️ Eliminando proyecto {project_id} para {email}", flush=True)

            try:
                response = self._request('DELETE', delete_url, headers=headers, json=delete_data)
                print(f"📨 [DELETE] Respuesta con json=: {response}", flush=True)
                print(f"📨 [DELETE] Tipo de respuesta: {type(response)}", flush=True)

                if isinstance(response, dict):
                    print(f"📨 [DELETE] Keys de respuesta: {list(response.keys())}", flush=True)
                    
                    if response.get('_id'):
                        print(f"🎉 [DELETE] PROYECTO ELIMINADO con json=: {response}", flush=True)
                        return {'success': True, 'deleted_project': response}
                    elif response.get('deleted') or response.get('success'):
                        print(f"🎉 [DELETE] Proyecto eliminado (formato alternativo): {response}", flush=True)
                        return {'success': True, 'deleted_project': response}
            
            except Exception as e:
                print(f"❌ [DELETE] Error con json=: {str(e)}", flush=True)
                print(f"❌ [DELETE] Continuando con data=...", flush=True)

            print(f"🗑️ Delete response: {response}", flush=True)
            if isinstance(response, dict) and response.get('_id'):
                return {'success': True, 'deleted_project': response}
            else:
                return {'success': False, 'error': 'Failed to delete project'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_current_timestamp(self):
        """Obtener timestamp actual en formato ISO"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    # 🔄 MÉTODOS DE COMPATIBILIDAD (para no romper código existente)
    
    def get_user_containers(self, email: str) -> dict:
        """Método de compatibilidad - ahora usa projects"""
        projects_result = self.get_user_projects(email)
        if projects_result['success']:
            # Renombrar 'projects' a 'containers' para compatibilidad
            projects_result['containers'] = projects_result.pop('projects')
        return projects_result

    def add_container_to_user(self, email: str, name: str, url: str, github_url: str, created_time:str) -> dict:
        """Método de compatibilidad - ahora usa create_project"""
        # project_id se ignora, se usa name como project_name
        return self.create_project(
            email=email,
            project_name=name,  # name se convierte en project_name
            url=url,
            github_url=github_url,
            created_time = created_time
        )

    def get_container_by_id(self, email: str, project_id: str) -> dict:
        """Método de compatibilidad - ahora busca por _id"""
        result = self.get_project_by_id(email, project_id)
        if result['success']:
            result['container'] = result.pop('project')
        return result

    def update_user_containers(self, email: str, containers: list) -> dict:
        """Método de compatibilidad - ya no aplica con la nueva estructura"""
        return {'success': False, 'error': 'This method is deprecated with the new projects table structure'}

container_service = ContainerService()