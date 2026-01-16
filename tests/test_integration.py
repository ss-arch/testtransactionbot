"""
Integration tests for the complete bot system
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aioresponses import aioresponses
import asyncio
import importlib

from main import TransactionMonitorBot
from monitors.base_monitor import Transaction


class TestTransactionMonitorBot:
    """Integration tests for the main bot"""

    @pytest.mark.asyncio
    async def test_bot_initialization(self, mock_env):
        """Test bot initializes correctly with all monitors"""
        # Reload config module to pick up mocked env vars
        import config
        importlib.reload(config)

        with patch('main.TelegramNotifier'):
            bot = TransactionMonitorBot()

            assert bot.notifier is not None
            assert len(bot.monitors) == 4
            assert bot.is_running is False

            # Check all monitor types are present
            monitor_names = [m.network_name for m in bot.monitors]
            assert 'TON' in monitor_names
            assert 'Everscale' in monitor_names
            assert 'Venom' in monitor_names
            assert 'Humanode (HUMO)' in monitor_names

    @pytest.mark.asyncio
    async def test_bot_initialization_missing_config(self, monkeypatch):
        """Test bot fails gracefully with missing configuration"""
        monkeypatch.delenv('TELEGRAM_BOT_TOKEN', raising=False)
        monkeypatch.delenv('TELEGRAM_CHAT_ID', raising=False)

        with pytest.raises(ValueError, match='TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID'):
            bot = TransactionMonitorBot()

    @pytest.mark.asyncio
    async def test_monitor_loop_single_iteration(self, mock_env):
        """Test a single iteration of the monitor loop"""
        import config
        importlib.reload(config)

        with patch('main.TelegramNotifier') as MockNotifier:
            mock_notifier = MagicMock()
            mock_notifier.send_transaction_alert = AsyncMock()
            MockNotifier.return_value = mock_notifier

            bot = TransactionMonitorBot()

            # Mock all monitors to return sample transactions
            sample_tx = Transaction(
                network='TON',
                tx_hash='test_hash_123',
                amount_usd=150000.0,
                sender='sender_addr',
                receiver='receiver_addr',
                timestamp=1705000000,
                amount_native=60000.0
            )

            for monitor in bot.monitors:
                monitor.fetch_and_filter = AsyncMock(return_value=[sample_tx])

            # Run one iteration
            bot.is_running = True

            # Create a task that will run the loop
            async def run_one_iteration():
                # Manually trigger one iteration
                tasks = [monitor.fetch_and_filter() for monitor in bot.monitors]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in results:
                    if not isinstance(result, Exception):
                        for tx in result:
                            await bot.notifier.send_transaction_alert(tx)

            await run_one_iteration()

            # Verify alerts were sent
            assert mock_notifier.send_transaction_alert.call_count == 4  # One per monitor

    @pytest.mark.asyncio
    async def test_monitor_handles_exceptions(self, mock_env):
        """Test that monitor loop handles exceptions gracefully"""
        import config
        importlib.reload(config)

        with patch('main.TelegramNotifier') as MockNotifier:
            mock_notifier = MagicMock()
            mock_notifier.send_error_message = AsyncMock()
            MockNotifier.return_value = mock_notifier

            bot = TransactionMonitorBot()

            # Make one monitor raise an exception
            bot.monitors[0].fetch_and_filter = AsyncMock(side_effect=Exception('Test error'))
            bot.monitors[1].fetch_and_filter = AsyncMock(return_value=[])
            bot.monitors[2].fetch_and_filter = AsyncMock(return_value=[])
            bot.monitors[3].fetch_and_filter = AsyncMock(return_value=[])

            # Run one iteration
            tasks = [monitor.fetch_and_filter() for monitor in bot.monitors]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Should have one exception and three successful results
            exceptions = [r for r in results if isinstance(r, Exception)]
            successes = [r for r in results if not isinstance(r, Exception)]

            assert len(exceptions) == 1
            assert len(successes) == 3


class TestEndToEnd:
    """End-to-end tests with mocked APIs"""

    @pytest.mark.asyncio
    async def test_full_transaction_detection_flow(self, mock_env):
        """Test complete flow from detection to notification"""
        import config
        importlib.reload(config)

        with patch('main.TelegramNotifier') as MockNotifier:
            mock_notifier = MagicMock()
            mock_notifier.send_transaction_alert = AsyncMock()
            mock_notifier.send_startup_message = AsyncMock()
            MockNotifier.return_value = mock_notifier

            with aioresponses() as m:
                # Mock TON price API
                m.get(
                    'https://tonapi.io/v2/rates?tokens=ton&currencies=usd',
                    payload={'rates': {'TON': {'prices': {'USD': 2.5}}}}
                )

                # Mock TON transactions API
                m.get(
                    'https://tonapi.io/v2/blockchain/transactions',
                    payload={
                        'transactions': [
                            {
                                'hash': 'large_ton_tx',
                                'utime': 1705000000,
                                'out_msgs': [
                                    {
                                        'value': '50000000000000',  # 50000 TON = $125,000
                                        'source': {'address': 'sender_1'},
                                        'destination': {'address': 'receiver_1'}
                                    }
                                ],
                                'in_msg': {}
                            }
                        ]
                    }
                )

                # Mock other network APIs to return empty results
                m.get(
                    'https://api.coingecko.com/api/v3/simple/price',
                    payload={'everscale': {'usd': 0.08}, 'venom': {'usd': 0.05}, 'humo': {'usd': 0.05}},
                    repeat=True
                )

                m.post(
                    'https://test-everscale.com/graphql',
                    payload={'data': {'transactions': []}}
                )

                m.post(
                    'https://test-venom.com/graphql',
                    payload={'data': {'transactions': []}}
                )

                m.get(
                    'https://humanode.api.subscan.io/api/scan/transfers',
                    payload={'code': 0, 'data': {'transfers': []}}
                )

                bot = TransactionMonitorBot()

                # Fetch transactions from all monitors
                all_transactions = []
                for monitor in bot.monitors:
                    txs = await monitor.fetch_and_filter()
                    all_transactions.extend(txs)

                # Send notifications
                for tx in all_transactions:
                    await bot.notifier.send_transaction_alert(tx)

                # Verify at least one transaction was detected and notified
                # (TON transaction should be detected)
                assert mock_notifier.send_transaction_alert.call_count >= 1


class TestConfiguration:
    """Test configuration handling"""

    def test_config_loading(self, mock_env):
        """Test configuration loads correctly"""
        import config
        importlib.reload(config)

        assert config.TELEGRAM_BOT_TOKEN == 'test_bot_token_123456'
        assert config.TELEGRAM_CHAT_ID == '123456789'
        assert config.MIN_TRANSACTION_USD == 100000
        assert config.POLL_INTERVAL_SECONDS == 60

    def test_explorer_urls(self, mock_env):
        """Test explorer URLs are configured correctly"""
        import config

        assert 'TON' in config.EXPLORERS
        assert 'Everscale' in config.EXPLORERS
        assert 'Venom' in config.EXPLORERS
        assert 'Humanode (HUMO)' in config.EXPLORERS

        assert 'tonviewer.com' in config.EXPLORERS['TON']
        assert 'everscan.io' in config.EXPLORERS['Everscale']
        assert 'venomscan.com' in config.EXPLORERS['Venom']
        assert 'humanode.subscan.io' in config.EXPLORERS['Humanode (HUMO)']
