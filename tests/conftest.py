"""
Pytest configuration and fixtures
"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing"""
    env_vars = {
        'TELEGRAM_BOT_TOKEN': 'test_bot_token_123456',
        'TELEGRAM_CHAT_ID': '123456789',
        'POLL_INTERVAL_SECONDS': '60',
        'MIN_TRANSACTION_USD': '100000',
        'TON_API_KEY': 'test_ton_api_key',
        'EVERSCALE_RPC_URL': 'https://test-everscale.com',
        'VENOM_RPC_URL': 'https://test-venom.com',
        'HUMANODE_RPC_URL': 'https://test-humanode.com'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram bot for testing"""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing"""
    return {
        'TON': {
            'hash': 'ton_hash_123abc',
            'value': 5000000000000,  # 5000 TON
            'sender': 'EQD7t1x8kl2s5',
            'receiver': 'UQB9ak3m4n7p',
            'timestamp': 1705000000,
            'price_usd': 2.5
        },
        'Everscale': {
            'id': 'ever_hash_456def',
            'value': '3000000000000',
            'src': '0:abc123',
            'dst': '0:def456',
            'now': 1705000000,
            'price_usd': 0.08
        },
        'Venom': {
            'id': 'venom_hash_789ghi',
            'value': '2000000000000',
            'src': '0:venom123',
            'dst': '0:venom456',
            'now': 1705000000,
            'price_usd': 0.05
        },
        'Humanode': {
            'hash': 'humo_hash_xyz',
            'amount': '2500000000000000000000',  # 2500 HUMO
            'from': 'humanode_address_1',
            'to': 'humanode_address_2',
            'block_timestamp': 1705000000,
            'price_usd': 0.05
        }
    }


@pytest.fixture
def mock_price_api_response():
    """Mock price API responses"""
    return {
        'ton': {'usd': 2.5},
        'everscale': {'usd': 0.08},
        'venom': {'usd': 0.05},
        'humo': {'usd': 0.05}
    }
