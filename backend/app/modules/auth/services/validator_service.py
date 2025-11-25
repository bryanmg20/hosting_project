import re

class AuthValidatorService:
    def __init__(self):
        self.email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def validate_email(self, email):
        return re.match(self.email_pattern, email) is not None
    
    def validate_password_length(self, password):
        """Valida que la contraseña tenga mínimo 8 caracteres."""
        return len(password) >= 8

    def validate_password_chars(self, password):
        """Valida mayúsculas, minúsculas, números y caracteres especiales."""
        pattern = (
            r'^(?=.*[a-z])'        
            r'(?=.*[A-Z])'         
            r'(?=.*\d)'            
            r'(?=.*[@$!%*?&._\-])' 
        )
        return re.search(pattern, password) is not None
    
    def validate_registration_data(self, data):
        if not data:
            return {'valid': False, 'error': 'No JSON data provided'}
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not all([email, password, name]):
            return {'valid': False, 'error': 'Email, password and name are required'}
        
        if not self.validate_email(email):
            return {'valid': False, 'error': 'Invalid email format'}
        
        if not self.validate_password_length(password):
            return {'valid': False, 'error': 'Password must be at least 8 characters long'}
        
        if not self.validate_password_chars(password):
            return {'valid': False, 'error': (
                    'Password must include uppercase, lowercase, number and special character.')}
        
        return {'valid': True, 'email': email, 'password': password, 'name': name}
    
    def validate_login_data(self, data):
        if not data:
            return {'valid': False, 'error': 'No JSON data provided'}
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return {'valid': False, 'error': 'Email and password are required'}
        
        return {'valid': True, 'email': email, 'password': password}