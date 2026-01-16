# Deployment Guide

Complete guide for deploying your transaction monitor bot to run 24/7.

---

## Option 1: Digital Ocean / VPS (Recommended) ⭐

### Prerequisites
- Ubuntu 20.04+ VPS
- Root or sudo access
- $5-10/month

### Step 1: Set Up Server

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Python and required tools
apt install -y python3 python3-pip git

# Install virtualenv
pip3 install virtualenv
```

### Step 2: Clone Repository

```bash
# Create app directory
mkdir -p /opt/bots
cd /opt/bots

# Clone your repository
git clone https://github.com/ss-arch/testtransactionbot.git
cd testtransactionbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Create .env file
cp .env.example .env
nano .env
```

Add your configuration:
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token
TELEGRAM_CHAT_ID=your_actual_chat_id
MIN_TRANSACTION_USD=100000
POLL_INTERVAL_SECONDS=60
TON_API_KEY=your_ton_api_key
```

Save and exit (Ctrl+X, Y, Enter)

### Step 4: Create Systemd Service

```bash
# Create service file
nano /etc/systemd/system/transaction-monitor.service
```

Add this content:
```ini
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

[Install]
WantedBy=multi-user.target
```

### Step 5: Start the Bot

```bash
# Reload systemd
systemctl daemon-reload

# Enable bot to start on boot
systemctl enable transaction-monitor

# Start the bot
systemctl start transaction-monitor

# Check status
systemctl status transaction-monitor

# View logs
journalctl -u transaction-monitor -f
```

### Useful Commands

```bash
# Stop bot
systemctl stop transaction-monitor

# Restart bot
systemctl restart transaction-monitor

# View logs (last 100 lines)
journalctl -u transaction-monitor -n 100

# Follow logs in real-time
journalctl -u transaction-monitor -f
```

---

## Option 2: Docker Deployment 🐳

### Step 1: Create Dockerfile

```bash
cd /Users/ss/my-app
nano Dockerfile
```

Add:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run bot
CMD ["python", "main.py"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  transaction-monitor:
    build: .
    container_name: transaction-monitor-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./bot.log:/app/bot.log
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Step 3: Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

---

## Option 3: Heroku (Free/Paid) 🟣

### Prerequisites
- Heroku account
- Heroku CLI installed

### Step 1: Create Procfile

```bash
cd /Users/ss/my-app
echo "worker: python main.py" > Procfile
```

### Step 2: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set TELEGRAM_CHAT_ID=your_chat_id
heroku config:set MIN_TRANSACTION_USD=100000
heroku config:set POLL_INTERVAL_SECONDS=60

# Deploy
git push heroku main

# Scale worker
heroku ps:scale worker=1

# View logs
heroku logs --tail
```

---

## Option 4: AWS EC2 ☁️

### Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2
2. Launch Instance:
   - AMI: Ubuntu 20.04
   - Type: t2.micro (free tier)
   - Configure security groups (allow SSH)
3. Download key pair

### Step 2: Connect and Deploy

```bash
# Connect to instance
ssh -i your-key.pem ubuntu@ec2-ip-address

# Follow "Option 1: VPS" steps above
```

---

## Option 5: Raspberry Pi / Local Server 🥧

### Requirements
- Raspberry Pi 4 (or any computer)
- Ubuntu/Raspbian OS

### Setup

```bash
# Clone repository
cd ~
git clone https://github.com/ss-arch/testtransactionbot.git
cd testtransactionbot

# Install dependencies
pip3 install -r requirements.txt

# Configure .env
cp .env.example .env
nano .env

# Run with screen (keeps running after disconnect)
screen -S transaction-monitor
python3 main.py

# Detach: Ctrl+A, D
# Reattach: screen -r transaction-monitor
```

### Auto-start on Boot (Raspberry Pi)

```bash
# Add to crontab
crontab -e

# Add this line:
@reboot cd /home/pi/testtransactionbot && /usr/bin/python3 main.py >> /home/pi/bot.log 2>&1
```

---

## Option 6: Railway.app 🚂

### Quick Deploy

1. Go to https://railway.app
2. Connect GitHub account
3. Select repository: `ss-arch/testtransactionbot`
4. Add environment variables
5. Deploy!

```bash
# Or use Railway CLI
npm i -g @railway/cli
railway login
railway init
railway up
```

---

## Monitoring & Maintenance

### Check Bot Health

```bash
# Check if bot is running
ps aux | grep main.py

# Check logs
tail -f bot.log

# Check system resources
htop
```

### Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/transaction-monitor

# Add:
/opt/bots/testtransactionbot/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
}
```

### Alerts

Set up monitoring with:
- **UptimeRobot** - Check if bot responds
- **Telegram notifications** - Bot sends startup/error messages
- **CloudWatch** (if using AWS)

---

## Troubleshooting

### Bot Not Starting

```bash
# Check logs
journalctl -u transaction-monitor -n 50

# Check Python errors
python3 main.py
```

### Memory Issues

```bash
# Check memory usage
free -h

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### API Rate Limits

```bash
# Increase polling interval in .env
POLL_INTERVAL_SECONDS=120
```

---

## Cost Comparison

| Provider | Cost/Month | Specs | Best For |
|----------|-----------|-------|----------|
| Digital Ocean | $5 | 1GB RAM, 1 CPU | Recommended ⭐ |
| AWS EC2 (t2.micro) | Free-$10 | 1GB RAM | Free tier |
| Heroku | Free-$7 | 512MB RAM | Quick start |
| Railway | Free-$5 | 512MB RAM | Easy deploy |
| Raspberry Pi | $0* | Varies | Home setup |
| VPS (Linode) | $5 | 1GB RAM | Alternative |

*Raspberry Pi: One-time hardware cost

---

## Recommended Setup (Production)

```bash
1. Ubuntu VPS (Digital Ocean) - $5/month
2. Systemd service (auto-restart)
3. Log rotation enabled
4. Firewall configured
5. Automatic updates enabled
6. Monitoring with UptimeRobot
```

### Security Best Practices

```bash
# Create non-root user
adduser botuser
usermod -aG sudo botuser

# Use non-root user in systemd service
[Service]
User=botuser
Group=botuser

# Set up firewall
ufw allow 22
ufw enable

# Keep system updated
apt update && apt upgrade -y
```

---

## Quick Start Commands

### Deploy to Digital Ocean (Complete)

```bash
# 1. Create droplet and SSH in
ssh root@your-ip

# 2. One-line install
curl -sSL https://raw.githubusercontent.com/ss-arch/testtransactionbot/main/deploy.sh | bash

# 3. Configure
nano /opt/bots/testtransactionbot/.env

# 4. Start
systemctl start transaction-monitor
```

---

## Need Help?

- Check logs: `journalctl -u transaction-monitor -f`
- Test manually: `python3 main.py`
- View status: `systemctl status transaction-monitor`

Your bot should now be running 24/7! 🚀
