import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Monitoring Configuration
POLL_INTERVAL_SECONDS = int(os.getenv('POLL_INTERVAL_SECONDS', 60))

# Network-specific token thresholds
NETWORK_THRESHOLDS = {
    'TON': 1000,  # 1,000 TON tokens
    'Everscale': 100000,  # 100,000 EVER tokens
    'Venom': 0  # Monitor all Venom transactions
}

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
