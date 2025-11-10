from flask import Blueprint, request, Response, jsonify
import requests
from urllib.parse import urljoin
import docker

dynamic_bp = Blueprint('dynamic_router', __name__)

try:
    docker_client = docker.from_env()
    docker_client.ping()
except Exception:
    docker_client = None

def get_container_url(container_name):
    if not docker_client:
        return None
        
    try:
        containers = docker_client.containers.list()
        
        for container in containers:
            if container.name == container_name:
                return f"http://{container_name}:80"
        
        return None
        
    except Exception:
        return None

@dynamic_bp.route('/', defaults={'path': ''})
@dynamic_bp.route('/<path:path>')
def handle_dynamic_request(path):
    if not docker_client:
        return jsonify({'error': 'Docker not available'}), 503
    
    host = request.host
    parts = host.replace('.localhost', '').split('.')
    
    if len(parts) == 2:
        project_name, service_name = parts
        container_name = f"{project_name}-{service_name}"
        container_url = get_container_url(container_name)
        
        if container_url is None:
            return jsonify({'error': 'Container not found'}), 404
        
        return proxy_to_container(container_url, path)
    
    return jsonify({'error': 'Invalid URL format'}), 400

def proxy_to_container(container_url, path):
    try:
        target_url = urljoin(container_url, path)
        if request.query_string:
            target_url += '?' + request.query_string.decode('utf-8')
        
        excluded_headers = ['host', 'content-length', 'content-encoding']
        headers = {
            key: value for key, value in request.headers
            if key.lower() not in excluded_headers
        }
        
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            timeout=30
        )
        
        response_headers = []
        for key, value in resp.headers.items():
            if key.lower() not in excluded_headers:
                response_headers.append((key, value))
        
        return Response(
            resp.iter_content(chunk_size=8192),
            status=resp.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection failed'}), 502
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500