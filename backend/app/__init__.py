# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from app.modules.sse.auto_shutdown_service import start_auto_shutdown_service
import os

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Null')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'Null')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes= 15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    app.config['ROBLE_DB_NAME'] = os.environ.get('ROBLE_DB_NAME', 'Null')
    
    # CORS: permitir específicamente ui.localhost y opcionalmente credenciales
    allowed_origins = ["http://ui.localhost", "http://localhost:3000"]
    CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)
    
    # Inicializar JWT
    jwt = JWTManager(app)
    
    # Configurar manejo de errores JWT
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return {'error': 'Missing or invalid token'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return {'error': 'Invalid token'}, 401

    @jwt.expired_token_loader
    def expired_token_callback(callback, callback_data):
        return {'error': 'Token has expired'}, 401

    # Registrar blueprints
    from app.modules.endpoints.auth_bp import auth_bp
    from app.modules.endpoints.project_routes import project_bp
    from app.modules.endpoints.container_routes import container_bp
    from app.modules.endpoints.see_routes import sse_bp
    from app.modules.endpoints.redirect import dynamic_bp

    app.register_blueprint(sse_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(container_bp)
    app.register_blueprint(dynamic_bp)
    
    # Iniciar servicio de auto-apagado por inactividad
   
    start_auto_shutdown_service()
    
    return app
