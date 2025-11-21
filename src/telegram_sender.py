"""
Enviar mensajes a Telegram con análisis de Perplexity
"""
import os
import requests
import re
from typing import Dict, Optional
from .config import PERPLEXITY_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from .youtube import get_transcript

def analyze_with_perplexity(transcript: str, title: str) -> Optional[str]:
    """
    Analizar transcripción con Perplexity Sonar Reasoning
    (Lógica adaptada de test_full_flow.py)
    """
    MAX_CHARS = 300000
    if len(transcript) > MAX_CHARS:
        print(f"  ⚠️ Transcripción muy larga ({len(transcript)} chars), truncando a {MAX_CHARS}...")
        transcript = transcript[:MAX_CHARS]
    
    PROMPT = f"""Eres un analista financiero experto. Analiza esta transcripción del video de José Luis Cárpatos.

TRANSCRIPCIÓN:
{transcript}

Genera el análisis con formato de tarjetas informativas:

📊 RESUMEN

[1 párrafo con los puntos más importantes, de 300-400 caracteres]

📈 NIVELES TÉCNICOS

S&P 500:
  🟢 Soporte ........ [X]
  🔴 Resistencia .... [X]
  📍 Actual ......... [X]

[Otros valores con formato similar]

📅 EVENTOS CLAVE

📌 [Fecha]: [Evento]

📌 [Fecha]: [Evento]
(Máximo 10 eventos)

🎯 SENTIMIENTO

Estado: [Muy optimista/Optimista/Neutral/Cauteloso/Muy Cauteloso]

Factores positivos:
  ✓ [Factor 1]
  ✓ [Factor 2]

Factores negativos:
  ✗ [Factor 1]
  ✗ [Factor 2]

⚡ Recomendación
[Consejo, no más de 300 caracteres]

Reglas:
- Ultra conciso
- Niveles con puntos para alineación
- Máximo 10 eventos
- Los eventos clave son aquellos programados en una fecha específica o rango de fechas, los eventos probabilísticos o históricos no se consideran
- Si no hay info, escribe "N/A"
"""
    
    try:
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'sonar-reasoning',
                'messages': [
                    {'role': 'user', 'content': PROMPT}
                ]
            },
            timeout=120
        )
        response.raise_for_status()
        
        response_data = response.json()
        analysis = response_data['choices'][0]['message']['content']
        
        # Limpiar tokens de razonamiento <think>...</think>
        analysis = re.sub(r'<think>.*?</think>', '', analysis, flags=re.DOTALL).strip()
        
        # Estadísticas
        usage = response_data.get('usage', {})
        cost = usage.get('cost', {})
        print(f"  💰 Tokens: {usage.get('total_tokens', 'N/A')} | Coste: ${cost.get('total_cost', 0):.4f}")
        
        return analysis
        
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ Error HTTP: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Detalles: {e.response.text}")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def send_analysis(video: Dict) -> bool:
    """
    Procesar video completo y enviar a Telegram
    Args:
        video: Dict con id, title, link, published
    Returns:
        True si se envió correctamente
    """
    try:
        print(f"  📝 Obteniendo transcripción...")
        transcript = get_transcript(video['id'])
        if not transcript:
            print(f"  ❌ No se pudo obtener transcripción")
            return False
        
        print(f"  📄 Transcripción obtenida: {len(transcript)} caracteres")
        
        print(f"  🧠 Analizando con Perplexity Sonar Reasoning...")
        analysis = analyze_with_perplexity(transcript, video['title'])
        if not analysis:
            print(f"  ❌ No se pudo obtener análisis")
            return False
        
        # Formatear mensaje
        message = f"""🎥 **Nuevo análisis de José Luis Cárpatos**

📹 {video['title']}
🔗 {video['link']}

---

{analysis}

---
_Análisis generado automáticamente por Perplexity Sonar Reasoning_
"""
        
        # Limitar a 4096 caracteres (límite de Telegram)
        if len(message) > 4096:
            print(f"  ⚠️ Mensaje muy largo ({len(message)} chars), truncando...")
            message = message[:4000] + "\n\n..._Mensaje truncado_"
        
        print(f"  📤 Enviando a Telegram...")
        telegram_response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            },
            timeout=30
        )
        telegram_response.raise_for_status()
        
        result = telegram_response.json()
        print(f"  ✅ Mensaje enviado (ID: {result['result']['message_id']})")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"  Detalles: {error_detail}")
            except:
                print(f"  Detalles: {e.response.text}")
        return False
