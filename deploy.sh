#!/bin/bash
# Quick deployment script for Ubuntu/Debian VPS

set -e

echo "=================================="
echo "Transaction Monitor Bot Deployment"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use: sudo bash deploy.sh)"
    exit 1
fi

# Update system
echo "📦 Updating system..."
apt update && apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt install -y python3 python3-pip python3-venv git

# Create directory
echo "📁 Creating application directory..."
mkdir -p /opt/bots
cd /opt/bots

# Clone repository
if [ -d "testtransactionbot" ]; then
    echo "📥 Updating repository..."
    cd testtransactionbot
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/ss-arch/testtransactionbot.git
    cd testtransactionbot
fi

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials!"
    echo "   nano /opt/bots/testtransactionbot/.env"
    echo ""
fi

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/transaction-monitor.service << 'EOF'
[Unit]
Description=Transaction Monitor Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bots/testtransactionbot
Environment="PATH=/opt/bots/testtransactionbot/venv/bin"
ExecStart=/opt/bots/testtransactionbot/venv/bin/python3 /opt/bots/testtransactionbot/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable transaction-monitor

echo ""
echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your bot:"
echo "   nano /opt/bots/testtransactionbot/.env"
echo ""
echo "2. Add your credentials:"
echo "   TELEGRAM_BOT_TOKEN=your_token"
echo "   TELEGRAM_CHAT_ID=your_chat_id"
echo ""
echo "3. Start the bot:"
echo "   systemctl start transaction-monitor"
echo ""
echo "4. Check status:"
echo "   systemctl status transaction-monitor"
echo ""
echo "5. View logs:"
echo "   journalctl -u transaction-monitor -f"
echo ""
echo "=================================="
