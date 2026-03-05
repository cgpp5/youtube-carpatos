import logging
import os
from datetime import datetime
from src.monitor import load_processed_ids, save_processed_ids
from src.youtube import get_new_videos
from src.telegram_sender import send_analysis

def setup_logging():
    """Configura el registro para guardar todo en monitor.log"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(base_dir, 'monitor.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler() # Mantiene la salida en consola
        ]
    )
    return logging.getLogger(__name__)

# 1. Inicializamos el logger globalmente
logger = setup_logging()

def run_check():
    """Ejecuta la comprobación de videos nuevos y los envía por Telegram"""
    now = datetime.now()
    logger.info(f"🔍 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando comprobación de Cárpatos...")
    
    try:
        # Cargar IDs procesados (memoria de lo que ya hemos visto)
        processed_ids = load_processed_ids()
        
        # Buscar nuevos videos
        new_videos = get_new_videos(processed_ids)
        
        if not new_videos:
            logger.info("✅ No se encontraron videos nuevos.")
            return

        logger.info(f"🎥 Encontrados {len(new_videos)} videos nuevos.")
        
        # Procesar cada video nuevo
        for video in new_videos:
            try:
                logger.info(f"📹 Procesando: {video['title']}")
                success = send_analysis(video)
                if success:
                    processed_ids.add(video['id'])
                    logger.info("✅ Enviado con éxito")
            except Exception as e:
                logger.error(f"❌ Error procesando video: {e}")
                continue
        
        # Guardar la lista actualizada de videos vistos
        save_processed_ids(processed_ids)
        logger.info("💾 Progreso guardado.")

    except Exception as e:
        logger.error(f"❌ Error crítico en run_check: {e}")

def main():
    try:
        run_check()
    finally:
        logger.info("--- Fin de la comprobación ---\n")

if __name__ == "__main__":
    main()