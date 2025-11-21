#!/usr/bin/env python3
"""
Monitor principal del canal de YouTube
"""
import time
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from .config import CHECKINTERVALHOURS, CACHEFILE, DATADIR
from .youtube import get_new_videos
from .telegram_sender import send_analysis

load_dotenv()

def load_processed_ids():
    """Cargar IDs procesados del cache"""
    if CACHEFILE.exists():
        with open(CACHEFILE, 'r') as f:
            data = json.load(f)
            return set(data.get('processed_videos', []))
    return set()

def save_processed_ids(processed_ids):
    """Guardar IDs procesados al cache"""
    DATADIR.mkdir(exist_ok=True)
    with open(CACHEFILE, 'w') as f:
        json.dump({
            'processed_videos': list(processed_ids),
            'last_updated': datetime.now().isoformat()
        }, f, indent=2)

def main():
    """Loop principal de monitoreo"""
    print(f"🚀 Iniciando monitor de YouTube")
    print(f"📺 Intervalo de chequeo: {CHECKINTERVALHOURS} horas")
    
    processed_ids = load_processed_ids()
    print(f"📝 Videos procesados previamente: {len(processed_ids)}")
    
    while True:
        try:
            print(f"\n🔍 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Chequeando nuevos videos...")
            
            # Obtener videos nuevos
            new_videos = get_new_videos(processed_ids)
            
            if not new_videos:
                print("✅ No hay videos nuevos")
            else:
                print(f"🎥 Encontrados {len(new_videos)} videos nuevos")
                
                for video in new_videos:
                    try:
                        print(f"\n📹 Procesando: {video['title']}")
                        
                        # Aquí iría la lógica completa de tu test_full_flow.py
                        # 1. Obtener transcripción
                        # 2. Analizar con Perplexity
                        # 3. Enviar a Telegram
                        
                        # Por ahora, usar send_analysis que deberás implementar
                        success = send_analysis(video)
                        
                        if success:
                            processed_ids.add(video['id'])
                            save_processed_ids(processed_ids)
                            print(f"✅ Video procesado correctamente")
                        else:
                            print(f"❌ Error procesando video")
                            
                    except Exception as e:
                        print(f"❌ Error procesando {video['id']}: {e}")
                        continue
            
            # Esperar hasta el próximo chequeo
            sleep_seconds = CHECKINTERVALHOURS * 3600
            print(f"\n😴 Esperando {CHECKINTERVALHOURS} horas hasta el próximo chequeo...")
            time.sleep(sleep_seconds)
            
        except KeyboardInterrupt:
            print("\n👋 Deteniendo monitor...")
            break
        except Exception as e:
            print(f"❌ Error en loop principal: {e}")
            print("⏳ Esperando 5 minutos antes de reintentar...")
            time.sleep(300)

if __name__ == "__main__":
    main()
