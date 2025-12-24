import json
from datetime import datetime
from .config import CACHE_FILE as CACHE_FILE_LOCAL

def load_processed_ids():
    """Cargar IDs procesados del archivo local cache.json"""
    try:
        # Usar la ruta definida en config.py que ya es compatible con Windows
        if CACHE_FILE_LOCAL.exists():
            with open(CACHE_FILE_LOCAL, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed_videos', []))
    except Exception as e:
        print(f"⚠️ Error cargando cache: {e}")
    
    return set()

def save_processed_ids(processed_ids):
    """Guardar IDs procesados en el archivo local"""
    try:
        data = {
            'processed_videos': list(processed_ids),
            'last_updated': datetime.now().isoformat()
        }
        
        # Asegurar que el directorio 'data' existe antes de intentar escribir
        CACHE_FILE_LOCAL.parent.mkdir(exist_ok=True)
        
        with open(CACHE_FILE_LOCAL, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Cache guardado localmente: {len(processed_ids)} videos")
    except Exception as e:
        print(f"❌ Error guardando cache local: {e}")
