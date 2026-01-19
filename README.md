# Multi-Network Transaction Monitor Bot

A Telegram bot that monitors large transactions across multiple blockchain networks: TON, Everscale, Venom, and Humanode (HUMO token). Configurable threshold (default: $100).

## Features

- 🔍 Monitors 4 blockchain networks simultaneously
- 💰 Alerts for transactions above configurable USD threshold
- 📱 Real-time notifications via Telegram
- 🔗 Direct links to blockchain explorers
- 📊 Shows transaction details: amount, sender, receiver, timestamp
- ⏱️ Configurable polling interval
- 🛡️ Duplicate transaction filtering
- 📝 Comprehensive logging
- ✅ Full test coverage with automated tests

## Networks Monitored

- **TON (The Open Network)** - Mainnet (TON token)
- **Everscale** - Mainnet (EVER token)
- **Venom** - Mainnet (VENOM token)
- **Humanode** - Mainnet (HUMO token)

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Your Telegram Chat ID

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Configure your `.env` file with your credentials (see Configuration section)

## Configuration

Edit the `.env` file with your settings:

### Required Settings

```env
# Get token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Get your chat ID from @userinfobot on Telegram
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Optional Settings

```env
# Monitoring settings
POLL_INTERVAL_SECONDS=60          # How often to check for new transactions (default: 60)
MIN_TRANSACTION_USD=100           # Minimum transaction value to alert in USD (default: 100)

# API Keys (optional but recommended for better rate limits)
TON_API_KEY=your_ton_api_key      # Get from https://tonconsole.com/

# Custom RPC endpoints (optional, defaults are provided)
EVERSCALE_RPC_URL=https://mainnet.evercloud.dev
VENOM_RPC_URL=https://jrpc.venom.foundation
HUMANODE_RPC_URL=https://explorer-rpc-http.mainnet.stages.humanode.io
```

## Getting Your Telegram Credentials

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided (looks like: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)
5. Paste it in your `.env` file as `TELEGRAM_BOT_TOKEN`

### 2. Get Your Chat ID

1. Start a chat with your newly created bot
2. Send any message to the bot
3. Open this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":123456789` in the response
5. Copy that number and paste it in your `.env` file as `TELEGRAM_CHAT_ID`

Alternative method:
1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send any message to get your user ID

## Usage

### Start the bot:

```bash
python main.py
```

The bot will:
1. Send a startup notification to your Telegram
2. Begin monitoring all configured networks
3. Send alerts when large transactions are detected
4. Log all activity to `bot.log` and console

### Stop the bot:

Press `Ctrl+C` to gracefully stop the bot.

## Testing

The bot includes a comprehensive test suite. To run tests:

```bash
# Install test dependencies (included in requirements.txt)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Or use the test runner script
chmod +x run_tests.sh
./run_tests.sh
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

## Transaction Alert Format

When a large transaction is detected, you'll receive a message like:

```
🚨 Large Transaction Detected!

💰 Amount: $125,450.00
   (2,500.0000 TON)

🌐 Network: TON

📤 From: EQD7t...x8kl2
📥 To: UQB9a...k3m4

🔗 Transaction: a1b2c3...d4e5f6

🕒 Time: 2026-01-16 15:30:45 UTC

🔍 View on Explorer
```

## API Rate Limits

### TON Network
- **Without API Key**: 1 request/second
- **With API Key**: Higher limits (recommended)
- Get your key at: https://tonconsole.com/

### Other Networks
- Use public RPC endpoints (default)
- For production, consider setting up your own nodes or using paid RPC services

## Troubleshooting

### Bot not sending messages
- Verify your `TELEGRAM_BOT_TOKEN` is correct
- Ensure you've started a chat with your bot (send `/start`)
- Check that `TELEGRAM_CHAT_ID` is correct

### No transactions detected
- Transactions above your threshold may be rare, be patient
- Lower the `MIN_TRANSACTION_USD` threshold for testing (e.g., set to 1 for testing)
- Check logs for any API errors
- Default threshold is $100 USD

### API Errors
- TON: Get an API key from https://tonconsole.com/
- Everscale/Venom: GraphQL endpoints may have rate limits
- Humanode: Consider using Subscan API for better reliability

### Connection Issues
- Check your internet connection
- Verify RPC endpoint URLs are accessible
- Look for errors in `bot.log`

## File Structure

```
.
├── main.py                      # Main bot entry point
├── config.py                    # Configuration loader
├── telegram_bot.py              # Telegram notification handler
├── requirements.txt             # Python dependencies
├── .env                         # Your configuration (not in git)
├── .env.example                 # Configuration template
├── bot.log                      # Runtime logs
├── README.md                    # This file
└── monitors/
    ├── __init__.py
    ├── base_monitor.py          # Base monitor class
    ├── ton_monitor.py           # TON network monitor
    ├── everscale_monitor.py     # Everscale network monitor
    ├── venom_monitor.py         # Venom network monitor
    └── humanode_monitor.py      # Humanode network monitor
```

## Customization

### Adding More Networks

1. Create a new monitor in `monitors/` directory
2. Inherit from `BaseMonitor` class
3. Implement `get_latest_transactions()` and `get_current_price_usd()` methods
4. Add the monitor to `main.py`

### Changing Alert Format

Edit the `format_transaction_message()` method in `telegram_bot.py`

### Adjusting Polling Interval

Change `POLL_INTERVAL_SECONDS` in your `.env` file (minimum 10 seconds recommended)

## Notes

- The bot stores the last 1000 transaction hashes to avoid duplicate alerts
- Prices are cached for 5 minutes to reduce API calls
- All networks are monitored independently and in parallel
- Errors are logged and sent to Telegram for monitoring

## Security

- Never commit your `.env` file to version control
- Keep your bot token secret
- Consider running the bot on a secure server
- Monitor the bot logs regularly

## License

MIT License - Feel free to modify and use as needed

## Support

For issues with:
- **TON**: https://ton.org/docs
- **Everscale**: https://docs.everscale.network/
- **Venom**: https://docs.venom.foundation/
- **Humanode**: https://docs.humanode.io/

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
