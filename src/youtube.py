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
    Obtener transcripción de un video de YouTube usando Evomi Proxy
    """
    import logging
    import os
    import time
    from youtube_transcript_api import YouTubeTranscriptApi
    
    try:
        # Pausa por seguridad
        time.sleep(5)
        
        # Configurar proxies de Evomi
        evomi_user = os.getenv("EVOMI_USER")
        evomi_pass = os.getenv("EVOMI_PASS")
        
        proxies = None
        if evomi_user and evomi_pass:
            # En Evomi, no especificar un parámetro de sesión (como _session-xyz) 
            # hace que cada petición use un proxy aleatorio por defecto.
            proxy_url = f"http://{evomi_user}:{evomi_pass}@rp.evomi.com:1000"
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            logging.info(f"🔄 Usando Evomi proxy random para el video {video_id}")
        else:
            logging.warning("⚠️ No se encontraron credenciales de Evomi en .env. Conectando sin proxy.")

        # Llamada a la API con proxy si está configurado
        if proxies:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
        else:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
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
        logging.error(f"❌ Error obteniendo transcripción para {video_id}: {e}")
        return None