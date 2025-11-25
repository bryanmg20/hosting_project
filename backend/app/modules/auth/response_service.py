from flask import jsonify

class AuthResponseService:
    @staticmethod
    def build_user_response(email, name, containers=None):
        return {
            'id': email,
            'email': email,
            'name': name,
            'containers': containers or []
        }
    
    @staticmethod
    def build_auth_response(user_data, access_token, refresh_token):
        return {
            'user': user_data,
            'token': access_token,
            'refresh_token': refresh_token
        }
    
    def auth_success(self, user_data, access_token, refresh_token, status_code=200):
        user_response = self.build_user_response(
            user_data['email'], 
            user_data['name'], 
            user_data.get('containers', [])
        )
        return jsonify(
            self.build_auth_response(user_response, access_token, refresh_token)
        ), status_code
    
    def error(self, message, status_code=400):
        return jsonify({'error': message}), status_code
    
    def user_info(self, user_data):
        user_response = self.build_user_response(
            user_data['email'],
            user_data['name'],
            user_data.get('containers', [])
        )
        return jsonify({'user': user_response}), 200