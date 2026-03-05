"""
Módulo para interactuar con YouTube
"""
import time
import feedparser
from datetime import datetime
from dateutil import parser as date_parser
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional
from .config import RSS_URL

def get_new_videos(processed_ids: set) -> List[Dict]:
    """
    Obtener videos nuevos del RSS feed
    Args:
        processed_ids: Set de IDs de videos ya procesados
    Returns:
        Lista de diccionarios con info de videos nuevos, filtrados por fecha actual
        y ordenados por fecha de publicación (más antiguos primero)
    """
    try:
        feed = feedparser.parse(RSS_URL)
        new_videos = []
        today = datetime.now().date()
        
        for entry in feed.entries:
            video_id = entry.yt_videoid
            if video_id not in processed_ids:
                # Parse the publication date
                published_dt = date_parser.parse(entry.published)
                published_date = published_dt.date()
                
                # Only include videos published today
                if published_date == today:
                    new_videos.append({
                        'id': video_id,
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.published,
                        '_published_dt': published_dt  # For sorting
                    })
        
        # Sort by publication date ascending (oldest first)
        new_videos.sort(key=lambda x: x['_published_dt'])
        
        # Remove the internal sorting key before returning
        for video in new_videos:
            del video['_published_dt']
        
        return new_videos
    except Exception as e:
        print(f"❌ Error obteniendo RSS: {e}")
        return []

def get_transcript(video_id: str) -> Optional[str]:
    """
    Obtener transcripción de un video de YouTube
    Args:
        video_id: ID del video de YouTube
    Returns:
        Transcripción completa como string, o None si falla
    """
    import os
    import time
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import GenericProxyConfig
    
    try:
        # Add delay to avoid YouTube rate limiting
        time.sleep(5)
        
        # Configurar proxies de Evomi
        evomi_user = os.getenv("EVOMI_USER")
        evomi_pass = os.getenv("EVOMI_PASS")
        
        proxy_config = None
        if evomi_user and evomi_pass:
            proxy_url = f"http://{evomi_user}:{evomi_pass}@rp.evomi.com:1000"
            # Inyectamos las credenciales usando la clase nativa de la librería
            proxy_config = GenericProxyConfig(
                http_url=proxy_url,
                https_url=proxy_url
            )
            print(f"🔄 Usando Evomi proxy random para el video {video_id}")
            
        # Instanciamos la API pasándole la configuración del proxy (si existe)
        if proxy_config:
            ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        else:
            ytt_api = YouTubeTranscriptApi()
            
        transcript_list = ytt_api.list(video_id)
        
        # Intentar español primero
        try:
            transcript = transcript_list.find_transcript(['es', 'es-ES', 'es-MX'])
        except:
            # Fallback a inglés
            transcript = transcript_list.find_transcript(['en'])
        
        transcript_data = transcript.fetch()
        raw_data = transcript_data.to_raw_data()
        full_transcript = ' '.join([segment['text'] for segment in raw_data])
        
        return full_transcript
    except Exception as e:
        print(f"❌ Error obteniendo transcripción para {video_id}: {e}")
        return None