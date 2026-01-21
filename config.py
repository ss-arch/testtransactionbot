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

# Known CEX (Centralized Exchange) addresses only
EXCHANGE_ADDRESSES = {
    'TON': {
        'EQBfAN7LfaUYgXZNw5Wc7GBgkEX2yhuJ5ka95J1JJwXXf4a8': 'Binance',
        'EQCjk1hh952vWaE9bRguFkAhDAL5jj3xj9p0uPWrFBq_GEMS': 'OKX',
        'EQBYivdc0GAk-nnczaMnYNuSjpeXu2nJS3DZ4KqLjosX5sVC': 'Bybit',
        'EQA0i8-CdGnF_DhUHHf92R1ONH6sIA9vLZ_WLcCIhfBBXwtG': 'KuCoin',
        'EQCA1W_I267-luVo9CzV7iCcrA1OO5vVeXD0QHACvBn0jKiH': 'Gate.io',
        'EQB5lISMH8vLxXpqWph7ZutCS4tU4QdZtrUUpmtgDCsO73JR': 'MEXC',
        'EQCzFTXpNNsFu8IgJnRnkDyBCL2ry8KgZYiDi3Jt31ie8EIQ': 'HTX (Huobi)',
        'EQABMMdzRuntgt9nfRB61qd1wR-cGPagXA3ReQazVYUNrT7p': 'Crypto.com',
        'EQDD8dqOzaj4zUK6ziJOo_G2lx6qf1TEktTRkFJ7T1c_fPQb': 'Bitfinex',
    },
    'Everscale': {
        # No major CEX for Everscale currently
    },
    'Venom': {
        # No major CEX for Venom currently
    }
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
