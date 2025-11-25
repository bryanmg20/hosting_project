import re

def extract_container_name_from_url(url: str) -> str:
    """
    Extraer el nombre del contenedor desde la URL
    """
    if not url:
        return 'default_id'
    
    # Tomar las primeras dos partes: proyecto.name → proyecto-name
    parts = url.split('.')
    if len(parts) >= 2:
        container_name = f"{parts[0]}-{parts[1]}"
    else:
        container_name = parts[0]
    
    container_name = re.sub(r'[^a-zA-Z0-9_-]', '', container_name)
    
    return container_name if container_name else 'default_id'
