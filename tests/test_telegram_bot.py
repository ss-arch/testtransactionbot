"""
Unit tests for Telegram bot functionality
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram_bot import TelegramNotifier
from monitors.base_monitor import Transaction


class TestTelegramNotifier:
    """Test Telegram notification functionality"""

    def test_init(self):
        """Test TelegramNotifier initialization"""
        notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')
        assert notifier.chat_id == '123456'
        assert notifier.bot is not None

    def test_shorten_address(self):
        """Test address shortening"""
        notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')

        # Long address should be shortened (first 8 + last 8)
        long_addr = 'EQD7t1x8kl2s5abc123def456ghi789'
        short_addr = notifier._shorten_address(long_addr)
        assert short_addr == 'EQD7t1x8...56ghi789'

        # Short address should remain unchanged
        short_input = 'EQD7t1x8'
        result = notifier._shorten_address(short_input)
        assert result == short_input

    def test_shorten_hash(self):
        """Test transaction hash shortening"""
        notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')

        # Hash shortening uses first 12 + last 12
        long_hash = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0'
        short_hash = notifier._shorten_hash(long_hash)
        assert short_hash == 'a1b2c3d4e5f6...o5p6q7r8s9t0'

    def test_get_token_symbol(self):
        """Test token symbol retrieval"""
        notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')

        assert notifier._get_token_symbol('TON') == 'TON'
        assert notifier._get_token_symbol('Everscale') == 'EVER'
        assert notifier._get_token_symbol('Venom') == 'VENOM'
        assert notifier._get_token_symbol('Humanode (HUMO)') == 'HUMO'
        assert notifier._get_token_symbol('Unknown') == 'TOKEN'

    def test_format_transaction_message(self):
        """Test transaction message formatting"""
        notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')

        tx = Transaction(
            network='TON',
            tx_hash='ton_hash_123abc456def',
            amount_usd=150000.0,
            sender='EQD7t1x8kl2s5abc123',
            receiver='UQB9ak3m4n7p456xyz',
            timestamp=1705000000,
            amount_native=60000.0
        )

        message = notifier.format_transaction_message(tx)

        # Check that all important info is in message
        assert '150,000.00' in message
        assert 'TON' in message
        assert '60,000.0000' in message
        assert 'ton_hash_12' in message  # Shortened hash
        assert 'EQD7t1x8' in message  # Part of sender
        assert 'UQB9ak3m' in message  # Part of receiver
        assert 'https://tonviewer.com/transaction/' in message

    def test_format_humo_transaction(self):
        """Test formatting of HUMO token transaction"""
        notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')

        tx = Transaction(
            network='Humanode (HUMO)',
            tx_hash='humo_hash_xyz',
            amount_usd=125000.0,
            sender='humanode_sender_123',
            receiver='humanode_receiver_456',
            timestamp=1705000000,
            amount_native=2500.0
        )

        message = notifier.format_transaction_message(tx)

        assert 'Humanode (HUMO)' in message
        assert 'HUMO' in message
        assert '125,000.00' in message
        assert '2,500.0000' in message
        assert 'humanode.subscan.io' in message

    @pytest.mark.asyncio
    async def test_send_transaction_alert(self, mock_telegram_bot):
        """Test sending transaction alert"""
        with patch('telegram_bot.Bot', return_value=mock_telegram_bot):
            notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')
            notifier.bot = mock_telegram_bot

            tx = Transaction(
                network='TON',
                tx_hash='ton_hash_123',
                amount_usd=150000.0,
                sender='sender_addr',
                receiver='receiver_addr',
                timestamp=1705000000,
                amount_native=60000.0
            )

            await notifier.send_transaction_alert(tx)

            # Verify bot.send_message was called
            mock_telegram_bot.send_message.assert_called_once()
            call_args = mock_telegram_bot.send_message.call_args

            assert call_args.kwargs['chat_id'] == '123456'
            assert call_args.kwargs['parse_mode'] == 'HTML'
            assert '150,000.00' in call_args.kwargs['text']

    @pytest.mark.asyncio
    async def test_send_startup_message(self, mock_telegram_bot):
        """Test sending startup message"""
        with patch('telegram_bot.Bot', return_value=mock_telegram_bot):
            notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')
            notifier.bot = mock_telegram_bot

            await notifier.send_startup_message()

            mock_telegram_bot.send_message.assert_called_once()
            call_args = mock_telegram_bot.send_message.call_args

            assert 'Transaction Monitor Bot Started' in call_args.kwargs['text']
            assert call_args.kwargs['chat_id'] == '123456'

    @pytest.mark.asyncio
    async def test_send_error_message(self, mock_telegram_bot):
        """Test sending error message"""
        with patch('telegram_bot.Bot', return_value=mock_telegram_bot):
            notifier = TelegramNotifier(bot_token='test_token', chat_id='123456')
            notifier.bot = mock_telegram_bot

            await notifier.send_error_message('Test error occurred')

            mock_telegram_bot.send_message.assert_called_once()
            call_args = mock_telegram_bot.send_message.call_args

            assert 'Test error occurred' in call_args.kwargs['text']
            assert 'Error' in call_args.kwargs['text']
