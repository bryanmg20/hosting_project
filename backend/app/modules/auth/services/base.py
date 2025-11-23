import requests
import os
import time

_tokens_store = {}

class BaseAuthService:

    def __init__(self, roble_db_name=None):
        self.auth_url = 'https://roble-api.openlab.uninorte.edu.co/auth'
        self.db_name = roble_db_name or os.environ.get('ROBLE_DB_NAME', 'not_founted')
        self.database_url = f"https://roble-api.openlab.uninorte.edu.co/database/{self.db_name}"


    def _request(self, method, url, **kwargs):
        """Método auxiliar para hacer peticiones HTTP"""
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    