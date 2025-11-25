
"""
Utilidades para la gestión de contenedores e imágenes Docker.
"""
from app.modules.sse.docker_service import docker_client


def cleanup_dangling_images():
    """
    Eliminar imágenes dangling (<none>) que quedan tras builds sin etiqueta.
    Se hace de forma best-effort: si falla algún remove se ignora.
    """
    try:
        dangling = docker_client.images.list(filters={'dangling': True})
        removed = 0
        for img in dangling:
            try:
                docker_client.images.remove(img.id, force=True)
                removed += 1
            except Exception:
                pass
        print(f"[CLEANUP] Dangling images removidas: {removed}", flush=True)
    except Exception as e:
        print(f"[CLEANUP][WARN] No se pudo limpiar dangling images: {e}", flush=True)
