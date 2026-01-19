import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Monitoring Configuration
POLL_INTERVAL_SECONDS = int(os.getenv('POLL_INTERVAL_SECONDS', 60))
MIN_TRANSACTION_USD = float(os.getenv('MIN_TRANSACTION_USD', 100))  # Default: $100 USD

# Explorer URLs (scraping sources)
EXPLORERS = {
    'TON': {
        'base': 'https://tonscan.org',
        'tx': 'https://tonscan.org/tx/'
    },
    'Everscale': {
        'base': 'https://everscan.io',
        'tx': 'https://everscan.io/transactions/'
    },
    'Venom': {
        'base': 'https://venomscan.com',
        'tx': 'https://venomscan.com/transactions/'
    }
}
