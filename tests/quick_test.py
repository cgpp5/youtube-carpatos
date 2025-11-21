#!/usr/bin/env python3
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Test Telegram
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

response = requests.post(url, json={
    "chat_id": chat_id,
    "text": "🚀 *Test exitoso*\n\n✅ Configuración correcta\n📱 Deployment próximamente",
    "parse_mode": "Markdown"
})

if response.status_code == 200:
    print("✅ Telegram funcionando!")
    print("📱 Revisa tu móvil")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
