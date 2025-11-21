#!/usr/bin/env python3
"""
Servidor HTTP para Google Cloud Run
"""
from flask import Flask, jsonify
import os
from datetime import datetime
from src.monitor import load_processed_ids, save_processed_ids
from src.youtube import get_new_videos
from src.telegram_sender import send_analysis

app = Flask(__name__)

@app.route('/')
def hello():
    return "YouTube Monitor Bot - Running on Cloud Run ✅"

@app.route('/monitor', methods=['GET', 'POST'])
def monitor():
    """Endpoint que ejecuta el monitoreo"""
    try:
        print(f"🚀 Monitoreo iniciado: {datetime.now().isoformat()}")
        
        # Cargar IDs procesados
        processed_ids = load_processed_ids()
        print(f"📝 Videos procesados: {len(processed_ids)}")
        
        # Obtener videos nuevos
        new_videos = get_new_videos(processed_ids)
        
        if not new_videos:
            print("✅ No hay videos nuevos")
            return jsonify({
                'status': 'success',
                'message': 'No hay videos nuevos',
                'processed': 0
            }), 200
        
        print(f"🎥 Encontrados {len(new_videos)} videos nuevos")
        processed_count = 0
        
        for video in new_videos:
            try:
                print(f"📹 Procesando: {video['title']}")
                success = send_analysis(video)
                
                if success:
                    processed_ids.add(video['id'])
                    processed_count += 1
                    print(f"✅ Video procesado")
            except Exception as e:
                print(f"❌ Error procesando {video['id']}: {e}")
                continue
        
        # Guardar IDs procesados
        save_processed_ids(processed_ids)
        
        return jsonify({
            'status': 'success',
            'message': f'Procesados {processed_count} videos',
            'processed': processed_count,
            'total_found': len(new_videos)
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
