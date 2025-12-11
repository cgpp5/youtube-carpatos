import os
import json
from datetime import datetime
from .config import CACHE_FILE

# Configuración de cache
USE_CLOUD_STORAGE = os.getenv('USE_CLOUD_STORAGE', 'false').lower() == 'true'
CACHE_FILE_LOCAL = CACHE_FILE

def load_processed_ids():
    """Cargar IDs procesados del cache"""
    try:
        if USE_CLOUD_STORAGE:
            # TODO: Implementar Google Cloud Storage
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(os.getenv('GCS_BUCKET_NAME'))
            blob = bucket.blob('processed_videos.json')
            data = json.loads(blob.download_as_string())
            return set(data.get('processed_videos', []))
        else:
            # Usar archivo local en /tmp
            if CACHE_FILE_LOCAL.exists():
                with open(CACHE_FILE_LOCAL, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_videos', []))
    except Exception as e:
        print(f"⚠️ Error cargando cache: {e}")
    
    return set()

def save_processed_ids(processed_ids):
    """Guardar IDs procesados al cache"""
    try:
        data = {
            'processed_videos': list(processed_ids),
            'last_updated': datetime.now().isoformat()
        }
        
        if USE_CLOUD_STORAGE:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(os.getenv('GCS_BUCKET_NAME'))
            blob = bucket.blob('processed_videos.json')
            blob.upload_from_string(json.dumps(data, indent=2))
        else:
            with open(CACHE_FILE_LOCAL, 'w') as f:
                json.dump(data, f, indent=2)
        
        print(f"✅ Cache guardado: {len(processed_ids)} videos")
    except Exception as e:
        print(f"❌ Error guardando cache: {e}")
