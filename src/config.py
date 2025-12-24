"""
Configuración centralizada del proyecto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde . env
load_dotenv()

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_FILE = DATA_DIR / "cache.json"

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)

# YouTube
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID', 'UCmJL2llHf2tEcDAjaz-LFgQ')
RSS_URL = f'https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}'

# LLM Configuration
LLM_MODEL = os.getenv('LLM_MODEL', 'sonar-reasoning')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')



