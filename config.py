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
    'TON': 10000,  # 10,000 TON tokens
    'Everscale': 100000,  # 100,000 EVER tokens
    'Venom': 100000  # 100,000 VENOM tokens
}

# Elector contract addresses to exclude (validator stake transactions)
ELECTOR_ADDRESSES = {
    'TON': [
        '-1:3333333333333333333333333333333333333333333333333333333333333333',
        'Ef8zMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzM0vF',  # Base64 format
    ],
    'Everscale': [
        '-1:3333333333333333333333333333333333333333333333333333333333333333',
    ],
    'Venom': [
        '-1:3333333333333333333333333333333333333333333333333333333333333333',
    ]
}

# Explorer URLs
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
