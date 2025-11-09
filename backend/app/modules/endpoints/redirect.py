from flask import Blueprint, request, redirect

dynamic_bp = Blueprint('dynamic_router', __name__)

@dynamic_bp.route('/redirect')
def handle_redirect():
    # Caddy mantiene el host original aquí
    host = request.host  # Ej: "proyecto1.bryan.localhost"
    
    print(f"Host recibido: {host}")
    
    # Subdominios dinámicos
    if host.endswith('.localhost'):
        project_name = host.replace('.localhost', '')
        container_name = project_name.replace('.', '-')
        target_url = f"http://{container_name}:5000"
        
        print(f"Redirigiendo {host} a {target_url}")
        return redirect(target_url, code=302)
    
    return {"error": "Subdominio no válido", "host": host}, 404