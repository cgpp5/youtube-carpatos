#!/bin/bash
# Script de deployment para Oracle Cloud

set -e  # Salir si hay algún error

echo "🚀 Iniciando deployment en Oracle Cloud..."

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Actualizar sistema
echo -e "${BLUE}📦 Actualizando sistema...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Instalar Python y dependencias del sistema
echo -e "${BLUE}🐍 Instalando Python y dependencias...${NC}"
sudo apt install -y python3 python3-pip python3-venv git

# 3. Crear directorio del proyecto
echo -e "${BLUE}📁 Configurando directorio del proyecto...${NC}"
mkdir -p ~/youtube-monitor
cd ~/youtube-monitor

# 4. Crear entorno virtual
echo -e "${BLUE}🔧 Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate

# 5. Instalar dependencias Python
echo -e "${BLUE}📚 Instalando dependencias Python...${NC}"
pip install --upgrade pip
pip install python-telegram-bot==20.7 \
            youtube-transcript-api==0.6.2 \
            feedparser==6.0.11 \
            requests==2.31.0 \
            python-dotenv==1.0.0

# 6. Crear estructura de directorios
mkdir -p data logs src

# 7. Crear archivo .env (tendrás que editarlo manualmente)
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Creando archivo .env...${NC}"
    cat > .env << 'EOF'
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Perplexity API
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# YouTube
YOUTUBE_CHANNEL_ID=UCYRxqvVMvPYDL0F35gJ9rjQ

# Config
CHECK_INTERVAL_HOURS=2
EOF
    echo -e "${RED}⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales:${NC}"
    echo -e "${RED}   nano ~/youtube-monitor/.env${NC}"
fi

# 8. Crear servicio systemd
echo -e "${BLUE}⚙️  Creando servicio systemd...${NC}"
sudo tee /etc/systemd/system/youtube-monitor.service > /dev/null << EOF
[Unit]
Description=YouTube Monitor Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/youtube-monitor
Environment="PATH=$HOME/youtube-monitor/venv/bin"
ExecStart=$HOME/youtube-monitor/venv/bin/python -u src/monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 9. Recargar systemd
sudo systemctl daemon-reload

echo -e "${GREEN}✅ Deployment completado!${NC}"
echo ""
echo -e "${BLUE}📋 Próximos pasos:${NC}"
echo "1. Sube tu código a ~/youtube-monitor/src/"
echo "2. Edita las credenciales: nano ~/youtube-monitor/.env"
echo "3. Inicia el servicio: sudo systemctl start youtube-monitor"
echo "4. Ver logs: sudo journalctl -u youtube-monitor -f"
echo "5. Habilitar inicio automático: sudo systemctl enable youtube-monitor"
