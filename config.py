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

# Known exchange addresses
EXCHANGE_ADDRESSES = {
    'TON': {
        # Major exchanges
        'EQBfAN7LfaUYgXZNw5Wc7GBgkEX2yhuJ5ka95J1JJwXXf4a8': 'Binance',
        'EQCjk1hh952vWaE9bRguFkAhDAL5jj3xj9p0uPWrFBq_GEMS': 'OKX',
        'EQBYivdc0GAk-nnczaMnYNuSjpeXu2nJS3DZ4KqLjosX5sVC': 'Bybit',
        'EQA0i8-CdGnF_DhUHHf92R1ONH6sIA9vLZ_WLcCIhfBBXwtG': 'KuCoin',
        'EQCA1W_I267-luVo9CzV7iCcrA1OO5vVeXD0QHACvBn0jKiH': 'Gate.io',
        'EQB5lISMH8vLxXpqWph7ZutCS4tU4QdZtrUUpmtgDCsO73JR': 'MEXC',
        'EQCzFTXpNNsFu8IgJnRnkDyBCL2ry8KgZYiDi3Jt31ie8EIQ': 'HTX (Huobi)',
        'EQABMMdzRuntgt9nfRB61qd1wR-cGPagXA3ReQazVYUNrT7p': 'Crypto.com',
        'EQDD8dqOzaj4zUK6ziJOo_G2lx6qf1TEktTRkFJ7T1c_fPQb': 'Bitfinex',
        # DEX
        'EQB3ncyBUTjZUA5EnFKR5_EnOMI9V1tTEAAPaiU71gc4TiUt': 'STON.fi',
        'EQBIlZX2URWkXCSg3QF2MJZU-wC5XkBoLww-hdWk2G37Jc6N': 'DeDust',
    },
    'Everscale': {
        # Major bridges and DEX
        '0:a519f99bb5d6d51ef958ed24d337ad75a1c770885dcd42d51d6663f9fcdacfb2': 'FlatQube DEX',
        '0:5eb5713ea9b4a0f3a13bc91b282cde809636eb1e68d2fcb6427571aca880177a': 'Octus Bridge',
    },
    'Venom': {
        # Venom DEX and bridges
        '0:5a3d46f40e59dab1fc1a0a0a4f8ca4f8a7a0e5c7d4b3a2918273645506070809': 'VenomSwap',
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
