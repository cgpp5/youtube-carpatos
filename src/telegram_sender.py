"""
Enviar mensajes a Telegram con análisis de Perplexity
"""
import os
import requests
from typing import Dict, Optional
from .config import PERPLEXITY_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def analyze_with_perplexity(video_url: str, title: str) -> Optional[str]:
    """
    Analiza directamente un vídeo de YouTube usando Perplexity Sonar Pro,
    delegando en el modelo la obtención del contenido del vídeo.
    """
    PROMPT =  f"""Eres un analista financiero experto. Analiza el contenido del siguiente vídeo de YouTube de José Luis Cárpatos:

{video_url}

El análisis debe basarse en el contenido completo del vídeo, no en la descripción.

Genera el análisis con formato de tarjetas informativas:

📊 RESUMEN

[1 párrafo con los puntos más importantes, de 300-400 caracteres]

📈 NIVELES TÉCNICOS

S&P 500:
  🟢 Soporte ........ [X]
  🔴 Resistencia .... [X]
  📍 Actual .......... [X]

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
[Dar consejo, no más de 300 caracteres]

Reglas:
- Lenguaje ultra conciso, preferir el uso del infinitivo y el lenguaje telegráfico
- No mencionar el número de caracteres
- Utilizar lenguaje impersonal sin referirse al autor del vídeo
- Niveles clave con puntos para su alineación
- Dentro de los niveles técnicos, si sólo se menciona el nivel actual de un valor pero no los soportes o resistencias entonces no incluir ese valor.
- Máximo 10 eventos
- Los eventos clave son aquellos programados en una fecha específica o rango de fechas, los eventos probabilísticos o históricos no se consideran, tampoco los anuncios de cuándo ciertas bolsas estarán abiertas o cerradas.
- Si no hay info, escribe "N/A"
- Máximo 5 factores positivos y 5 negativos
"""

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sonar-pro",
                "messages": [
                    {"role": "user", "content": PROMPT}
                ],
            },
            timeout=120,
        )
        response.raise_for_status()

        data = response.json()
        analysis = data["choices"][0]["message"]["content"]

        usage = data.get("usage", {})
        cost = usage.get("cost", {})
        print(
            f"💰 Tokens: {usage.get('total_tokens', 'N/A')} | "
            f"Coste: ${cost.get('total_cost', 0):.4f}"
        )

        return analysis

    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP en Perplexity: {e}")
        if e.response is not None:
            print(f"Detalles: {e.response.text}")
        return None

    except Exception as e:
        print(f"❌ Error analizando vídeo con Perplexity: {e}")
        return None

def format_to_html(text: str) -> str:
    """Convierte Markdown básico de la IA a HTML simple"""
    # Escapar caracteres HTML primero para seguridad
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Convertir negritas de Markdown (**) a HTML (<b>)
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text
    
def send_analysis(video: Dict) -> bool:
    try:
        print("🧠 Analizando vídeo directamente con Perplexity...")
        analysis = analyze_with_perplexity(video['link'], video['title'])
        if not analysis:
            return False

        safe_analysis = format_to_html(analysis)
        message = f"""🎬<b>{video['title']}</b>

{video['link']}

{safe_analysis}
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
                "parse_mode": "HTML",
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






