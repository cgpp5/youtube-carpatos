#!/usr/bin/env python3
from flask import Flask, jsonify
import os
from datetime import datetime
from src.monitor import load_processed_ids, save_processed_ids
from src.youtube import get_new_videos
from src.telegram_sender import send_analysis

app = Flask(__name__)

def should_check_now():
    """Decide si debe hacer el chequeo según la hora (CET)"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    weekday = now.weekday()  # 0=Lunes, 6=Domingo
    
    # Solo lunes a viernes
    if weekday >= 5:  # Sábado o Domingo
        return False
    
    # Alta intensidad: 8:30-11:00 y 16:00-18:30 (cada 3 min)
    if (hour == 8 and minute >= 30) or (9 <= hour < 11):
        return True
    if (16 <= hour < 18) or (hour == 18 and minute < 30):
        return True
    
    # Baja intensidad: 11:00-16:00 (cada 15 min)
    if 11 <= hour < 16:
        return minute % 15 == 0
    
    return False

@app.route('/')
def home():
    return "✅ YouTube Monitor Bot - José Luis Cárpatos"

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/cache')
def view_cache():
    """Ver IDs procesados en el cache"""
    try:
        processed_ids = load_processed_ids()
        return jsonify({
            'total': len(processed_ids),
            'ids': list(processed_ids)
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/monitor')
def monitor():
    """Ejecuta el monitoreo con lógica de horarios inteligente"""
    now = datetime.now()
    
    if not should_check_now():
        return jsonify({
            'status': 'skipped',
            'message': 'Fuera de horario de monitoreo',
            'time': now.strftime('%H:%M'),
            'day': now.strftime('%A')
        }), 200
    
    try:
        print(f"🔍 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Chequeando videos...")
        
        processed_ids = load_processed_ids()
        new_videos = get_new_videos(processed_ids)
        
        if not new_videos:
            print("✅ No hay videos nuevos")
            return jsonify({
                'status': 'success',
                'message': 'No hay videos nuevos',
                'processed': 0,
                'time': now.strftime('%H:%M')
            })
        
        print(f"🎥 Encontrados {len(new_videos)} videos nuevos")
        processed_count = 0
        
        for video in new_videos:
            try:
                print(f"📹 Procesando: {video['title']}")
                success = send_analysis(video)
                if success:
                    processed_ids.add(video['id'])
                    processed_count += 1
                    print(f"✅ Procesado correctamente")
            except Exception as e:
                print(f"❌ Error procesando video: {e}")
                continue
        
        save_processed_ids(processed_ids)
        
        return jsonify({
            'status': 'success',
            'processed': processed_count,
            'total_found': len(new_videos),
            'time': now.strftime('%H:%M')
        })
        
    except Exception as e:
        print(f"❌ Error en monitor: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'time': now.strftime('%H:%M')
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Bot iniciado en puerto {port}")
    app.run(host='0.0.0.0', port=port)
