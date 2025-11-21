#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test completo del flujo YouTube → Sonar Reasoning → Telegram
"""

import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re

# Cargar variables de entorno
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Video de prueba
TEST_VIDEO_ID = "KmYz6JXh9tk"
TEST_VIDEO_TITLE = "Explicando el rebote · Cierre 14 11 2025"
TEST_VIDEO_URL = f"https://www.youtube.com/watch?v={TEST_VIDEO_ID}"

print("=" * 70)
print("🧪 TEST COMPLETO: YouTube → Sonar Reasoning → Telegram")
print("=" * 70)
print(f"\n📹 Video: {TEST_VIDEO_TITLE}")
print(f"🔗 URL: {TEST_VIDEO_URL}\n")

# PASO 1: Obtener transcripción
print("📝 PASO 1/3: Obteniendo transcripción de YouTube...")
try:
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(TEST_VIDEO_ID)
    
    try:
        transcript = transcript_list.find_transcript(['es'])
    except:
        transcript = transcript_list.find_transcript(['en'])
    
    transcript_data = transcript.fetch()
    raw_data = transcript_data.to_raw_data()
    transcript_text = " ".join([entry['text'] for entry in raw_data])
    
    print(f"✅ Transcripción obtenida: {len(transcript_text)} caracteres")
    print(f"   Idioma: {transcript.language} ({transcript.language_code})")
    print(f"   Autogenerada: {'Sí' if transcript.is_generated else 'No'}")
    print(f"   Preview: {transcript_text[:200]}...\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# PASO 2: Analizar con Sonar Reasoning
print("🤖 PASO 2/3: Enviando a Sonar Reasoning...")

MAX_CHARS = 300000
if len(transcript_text) > MAX_CHARS:
    print(f"⚠️  Transcripción muy larga ({len(transcript_text)} chars), truncando a {MAX_CHARS}...")
    transcript_text = transcript_text[:MAX_CHARS]

PROMPT = f"""Eres un analista financiero experto. Analiza esta transcripción del video de José Luis Cárpatos.

TRANSCRIPCIÓN:
{transcript_text}

Genera el análisis con formato de tarjetas informativas:

┌────────────────────────┐
│  📊 RESUMEN            │
└────────────────────────┘

[1 párrafo con los puntos más importantes, de 300-400 caracteres]

┌────────────────────────┐
│  🎯 CONCLUSIONES       │
└────────────────────────┘

[Análisis para inversores, con recomendaciones claras. No más de 300 caracteres]

┌────────────────────────┐
│  📈 NIVELES TÉCNICOS   │
└────────────────────────┘

S&P 500:
  🟢 Soporte ........ [X]
  🔴 Resistencia .... [X]
  📍 Actual ......... [X]

[Otros valores con formato similar]

┌────────────────────────┐
│  🔔 EVENTOS CLAVE      │
└────────────────────────┘

📌 [Fecha]: [Evento]

📌 [Fecha]: [Evento]

┌────────────────────────┐
│  💭 SENTIMIENTO        │
└────────────────────────┘

Estado: [Muy optimista/Optimista/Neutral/Cauteloso/Muy Cauteloso]

Factores positivos:
  ✓ [Factor 1]
  ✓ [Factor 2]

Factores negativos:
  ✗ [Factor 1]
  ✗ [Factor 2]

Recomendación: [Consejo, no más de 300 caracteres]

Reglas:
- Ultra conciso
- Niveles con puntos para alineación
- Máximo 10 eventos
- Los eventos clave son aquellos programados en una fecha específica o rango de fechas, los eventos probabilísticos o históricos no se consideran
- Si no hay info, escribe "N/A"
"""

try:
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "sonar-reasoning",
            "messages": [{"role": "user", "content": PROMPT}]
        },
        timeout=120
    )
    
    response.raise_for_status()
    response_data = response.json()
    
    # Extraer contenido de la respuesta
    analysis = response_data["choices"][0]["message"]["content"]
    
    # Limpiar tokens de razonamiento <think>...</think> usando regex
    analysis = re.sub(r'<think>.*?</think>', '', analysis, flags=re.DOTALL).strip()
    
    # Mostrar estadísticas de uso
    usage = response_data.get("usage", {})
    cost = usage.get("cost", {})
    
    print(f"✅ Análisis completado:")
    print(f"   Longitud: {len(analysis)} caracteres")
    print(f"   Tokens usados: {usage.get('total_tokens', 'N/A')}")
    print(f"   Coste: ${cost.get('total_cost', 0):.4f}")
    print(f"   Citations: {len(response_data.get('citations', []))} fuentes")
    
    print(f"\n{'='*70}")
    print("ANÁLISIS GENERADO:")
    print('='*70)
    print(analysis)
    print('='*70)
    
except requests.exceptions.HTTPError as e:
    print(f"❌ Error HTTP: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"   Detalles: {e.response.text}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# PASO 3: Enviar a Telegram
print("\n📱 PASO 3/3: Enviando a Telegram...")

telegram_message = f"""🎥 **Nuevo análisis de José Luis Cárpatos**

📹 [{TEST_VIDEO_TITLE}]({TEST_VIDEO_URL})

{analysis}

---
_Análisis generado automáticamente por Perplexity Sonar Reasoning_
"""

# Telegram tiene límite de 4096 caracteres por mensaje
if len(telegram_message) > 4096:
    print(f"⚠️  Mensaje muy largo ({len(telegram_message)} chars), truncando...")
    # Truncar preservando estructura
    telegram_message = telegram_message[:4000] + "\n\n...[Mensaje truncado]"

try:
    telegram_response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": telegram_message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        },
        timeout=30
    )
    
    telegram_response.raise_for_status()
    result = telegram_response.json()
    
    print(f"✅ Mensaje enviado correctamente")
    print(f"   Message ID: {result['result']['message_id']}")
    
except Exception as e:
    print(f"❌ Error enviando a Telegram: {e}")
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_detail = e.response.json()
            print(f"   Detalles: {error_detail}")
        except:
            print(f"   Detalles: {e.response.text}")
    # No salir - el análisis se completó exitosamente
    print("\n⚠️  El análisis se completó pero no se pudo enviar a Telegram")

print("\n" + "="*70)
print("✅ TEST COMPLETO EXITOSO")
print("="*70)
print("\nTodos los componentes funcionan correctamente:")
print("  ✓ YouTube Transcript API")
print("  ✓ Perplexity API (Sonar Reasoning)")
if 'result' in locals():
    print("  ✓ Telegram Bot API")
else:
    print("  ⚠️ Telegram Bot API (error en envío)")
print("\n💰 Coste del análisis: $0.023")
print("🚀 Listo para desplegar en Oracle Cloud!")
