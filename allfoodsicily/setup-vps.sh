#!/bin/bash
# Setup script for AllFoodSicily Bot on VPS (Hetzner, Contabo, etc.)
# Usage: bash setup-vps.sh

set -e

echo "🚀 AllFoodSicily Bot - VPS Setup Script"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "📦 Installing system dependencies..."
apt install -y python3.10 python3-pip python3-venv git curl wget

# Create app user
echo "👤 Creating application user..."
if ! id "allfoodsicily" &>/dev/null; then
    useradd -m -s /bin/bash allfoodsicily
    echo "✅ User 'allfoodsicily' created"
else
    echo "ℹ️  User 'allfoodsicily' already exists"
fi

# Create app directory
APP_DIR="/opt/allfoodsicily"
echo "📁 Creating application directory: $APP_DIR"
mkdir -p $APP_DIR
chown allfoodsicily:allfoodsicily $APP_DIR

# Clone or copy project
echo "📥 Setting up project files..."
if [ -d ".git" ]; then
    echo "ℹ️  Git repository detected, please clone manually:"
    echo "   git clone <your-repo-url> $APP_DIR"
    echo "   Then run this script again or continue manually"
    read -p "Press Enter to continue..."
else
    echo "📋 Copying files to $APP_DIR..."
    cp -r . $APP_DIR/
    chown -R allfoodsicily:allfoodsicily $APP_DIR
fi

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd $APP_DIR
sudo -u allfoodsicily python3 -m venv venv
sudo -u allfoodsicily $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u allfoodsicily $APP_DIR/venv/bin/pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "$APP_DIR/.env" ]; then
    echo "📝 Creating .env file template..."
    sudo -u allfoodsicily cp env.example $APP_DIR/.env
    echo ""
    echo "${YELLOW}⚠️  IMPORTANT: Edit $APP_DIR/.env and add your API keys!${NC}"
    echo "   nano $APP_DIR/.env"
    echo ""
    read -p "Press Enter after editing .env..."
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p $APP_DIR/logs
chown allfoodsicily:allfoodsicily $APP_DIR/logs

# Create systemd service
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/allfoodsicily.service <<EOF
[Unit]
Description=AllFoodSicily Telegram Bot
After=network.target

[Service]
Type=simple
User=allfoodsicily
Group=allfoodsicily
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=allfoodsicily

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable service
echo "✅ Systemd service created"
echo ""
echo "📋 Service management commands:"
echo "   ${GREEN}sudo systemctl start allfoodsicily${NC}    - Start bot"
echo "   ${GREEN}sudo systemctl stop allfoodsicily${NC}     - Stop bot"
echo "   ${GREEN}sudo systemctl restart allfoodsicily${NC}  - Restart bot"
echo "   ${GREEN}sudo systemctl status allfoodsicily${NC}   - Check status"
echo "   ${GREEN}sudo systemctl enable allfoodsicily${NC}   - Enable on boot"
echo "   ${GREEN}sudo journalctl -u allfoodsicily -f${NC}   - View logs"
echo ""

# Setup log rotation
echo "📋 Setting up log rotation..."
cat > /etc/logrotate.d/allfoodsicily <<EOF
$APP_DIR/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 allfoodsicily allfoodsicily
    sharedscripts
    postrotate
        systemctl reload allfoodsicily > /dev/null 2>&1 || true
    endscript
}
EOF

echo "✅ Log rotation configured"
echo ""

# Final instructions
echo "========================================"
echo "${GREEN}✅ Setup completed!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit environment variables:"
echo "   ${YELLOW}sudo nano $APP_DIR/.env${NC}"
echo ""
echo "2. Validate configuration:"
echo "   ${YELLOW}sudo -u allfoodsicily $APP_DIR/venv/bin/python $APP_DIR/main.py --validate${NC}"
echo ""
echo "3. Start the bot:"
echo "   ${GREEN}sudo systemctl start allfoodsicily${NC}"
echo "   ${GREEN}sudo systemctl enable allfoodsicily${NC}"
echo ""
echo "4. Check status:"
echo "   ${GREEN}sudo systemctl status allfoodsicily${NC}"
echo ""
echo "5. View logs:"
echo "   ${GREEN}sudo journalctl -u allfoodsicily -f${NC}"
echo ""

