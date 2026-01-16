# Quick Start Guide

Get your Transaction Monitor Bot running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Create Your Telegram Bot

1. Open Telegram and find [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Choose a name and username for your bot
4. Copy the bot token (format: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)

## Step 3: Get Your Chat ID

**Option A: Using @userinfobot**
1. Find [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send any message
3. Copy your user ID

**Option B: Using your bot**
1. Start a chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find `"chat":{"id":123456789` and copy that number

## Step 4: Configure the Bot

```bash
# Copy the example config
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use any text editor
```

Minimum required configuration:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Step 5: Run the Bot

```bash
python main.py
```

You should receive a startup message in Telegram!

## Optional: Get API Keys for Better Performance

### TON API Key (Recommended)
1. Visit [TON Console](https://tonconsole.com/)
2. Create an account
3. Generate an API key
4. Add to `.env`: `TON_API_KEY=your_key_here`

## Testing the Bot

### Run Tests
```bash
pytest
```

### Lower Threshold for Testing
To see more transactions during testing, edit `.env`:
```env
MIN_TRANSACTION_USD=1000  # Lower threshold (default: 100000)
POLL_INTERVAL_SECONDS=30  # Faster polling (default: 60)
```

## Troubleshooting

### Bot doesn't send messages
- Check your bot token is correct
- Ensure you started a chat with your bot
- Verify your chat ID is correct

### No transactions detected
- Large transactions ($100k+) are rare
- Lower `MIN_TRANSACTION_USD` for testing
- Check logs: `tail -f bot.log`

### API errors
- Get a TON API key from https://tonconsole.com/
- Check your internet connection
- Review logs for specific errors

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- See [TESTING.md](TESTING.md) for testing guide
- Customize polling interval and threshold in `.env`
- Run the bot as a service (systemd, Docker, etc.)

## Running in Production

### As a Background Process
```bash
nohup python main.py > output.log 2>&1 &
```

### Using screen
```bash
screen -S tx-monitor
python main.py
# Press Ctrl+A then D to detach
```

### Using Docker (Coming Soon)
```bash
docker build -t tx-monitor .
docker run -d --env-file .env tx-monitor
```

## Need Help?

Check the logs:
```bash
tail -f bot.log
```

Run in verbose mode:
```bash
# Edit main.py, change logging level to DEBUG
logging.basicConfig(level=logging.DEBUG, ...)
```

## Example Transaction Alert

When a large transaction is detected, you'll receive:

```
🚨 Large Transaction Detected!

💰 Amount: $125,450.00
   (2,500.0000 HUMO)

🌐 Network: Humanode (HUMO)

📤 From: humanode...address1
📥 To: humanode...address2

🔗 Transaction: humo_has...xyz

🕒 Time: 2026-01-16 15:30:45 UTC

🔍 View on Explorer
```

Happy monitoring! 🚀
