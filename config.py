import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Monitoring Configuration
POLL_INTERVAL_SECONDS = int(os.getenv('POLL_INTERVAL_SECONDS', 60))
MIN_TRANSACTION_USD = float(os.getenv('MIN_TRANSACTION_USD', 100))  # Default: $100 USD

# API Configuration
TON_API_KEY = os.getenv('TON_API_KEY', '')
EVERSCALE_RPC_URL = os.getenv('EVERSCALE_RPC_URL', 'https://mainnet.evercloud.dev')
VENOM_RPC_URL = os.getenv('VENOM_RPC_URL', 'https://jrpc.venom.foundation')
HUMANODE_RPC_URL = os.getenv('HUMANODE_RPC_URL', 'https://explorer-rpc-http.mainnet.stages.humanode.io')

# Explorer URLs
EXPLORERS = {
    'TON': 'https://tonviewer.com/transaction/',
    'Everscale': 'https://everscan.io/transactions/',
    'Venom': 'https://venomscan.com/transactions/',
    'Humanode (HUMO)': 'https://humanode.subscan.io/extrinsic/'
}
