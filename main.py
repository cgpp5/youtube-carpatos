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
    """Tu función original, ahora registrando cada paso"""
    logger.info("--- Iniciando comprobación de Cárpatos ---")
    try:
        # --- AQUÍ VA EL CONTENIDO EXACTO DE TU run_check ACTUAL ---
        # Solo tienes que sustituir los comandos 'print' por 'logger.info'
        
        # Ejemplo de tu lógica interna:
        # videos_nuevos = check_videos()
        # if not videos_nuevos:
        #     logger.info("✅ No new videos found.")
        # else:
        #     logger.info(f"🎥 Found {len(videos_nuevos)} new videos. Analizando...")
        #     # ... código de envío ...
        #     logger.info("✅ Mensaje enviado a Telegram.")
        
        pass # Reemplaza este pass con tu código real
        
    except Exception as e:
        # Atrapa y registra cualquier error inesperado
        logger.error(f"❌ Error crítico en run_check: {e}")

def main():
    try:
        run_check()
    finally:
        logger.info("--- Fin de la comprobación ---\n")

if __name__ == "__main__":
    main()