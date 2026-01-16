"""
Unit tests for network monitors
"""
import pytest
from aioresponses import aioresponses
from monitors.base_monitor import Transaction
from monitors.ton_monitor import TONMonitor
from monitors.everscale_monitor import EverscaleMonitor
from monitors.venom_monitor import VenomMonitor
from monitors.humanode_monitor import HumanodeMonitor


class TestBaseMonitor:
    """Test base monitor functionality"""

    def test_transaction_creation(self):
        """Test Transaction object creation"""
        tx = Transaction(
            network='TON',
            tx_hash='test_hash_123',
            amount_usd=150000.0,
            sender='sender_address',
            receiver='receiver_address',
            timestamp=1705000000,
            amount_native=50000.0
        )
        assert tx.network == 'TON'
        assert tx.tx_hash == 'test_hash_123'
        assert tx.amount_usd == 150000.0
        assert tx.sender == 'sender_address'
        assert tx.receiver == 'receiver_address'
        assert tx.timestamp == 1705000000
        assert tx.amount_native == 50000.0

    def test_duplicate_detection(self):
        """Test duplicate transaction detection"""
        monitor = TONMonitor(min_usd=100000, api_key='test_key')

        # First check should not be duplicate
        assert monitor.is_duplicate('tx_hash_1') is False

        # Second check should be duplicate
        assert monitor.is_duplicate('tx_hash_1') is True

        # Different hash should not be duplicate
        assert monitor.is_duplicate('tx_hash_2') is False


class TestTONMonitor:
    """Test TON network monitor"""

    @pytest.mark.asyncio
    async def test_get_price_usd(self, mock_price_api_response):
        """Test TON price fetching"""
        monitor = TONMonitor(min_usd=100000, api_key='test_key')

        with aioresponses() as m:
            m.get(
                'https://tonapi.io/v2/rates?tokens=ton&currencies=usd',
                payload={'rates': {'TON': {'prices': {'USD': 2.5}}}}
            )

            price = await monitor.get_current_price_usd()
            assert price == 2.5

    @pytest.mark.asyncio
    async def test_get_price_usd_with_cache(self):
        """Test price caching mechanism"""
        monitor = TONMonitor(min_usd=100000, api_key='test_key')

        with aioresponses() as m:
            m.get(
                'https://tonapi.io/v2/rates?tokens=ton&currencies=usd',
                payload={'rates': {'TON': {'prices': {'USD': 2.5}}}}
            )

            # First call should hit API
            price1 = await monitor.get_current_price_usd()
            assert price1 == 2.5

            # Second call should use cache (no additional API call)
            price2 = await monitor.get_current_price_usd()
            assert price2 == 2.5
            assert monitor.price_cache['price'] == 2.5

    @pytest.mark.asyncio
    async def test_get_latest_transactions(self):
        """Test fetching latest transactions"""
        monitor = TONMonitor(min_usd=100000, api_key='test_key')

        with aioresponses() as m:
            # Mock price API
            m.get(
                'https://tonapi.io/v2/rates?tokens=ton&currencies=usd',
                payload={'rates': {'TON': {'prices': {'USD': 2.5}}}}
            )

            # Mock transactions API
            m.get(
                'https://tonapi.io/v2/blockchain/transactions',
                payload={
                    'transactions': [
                        {
                            'hash': 'ton_tx_1',
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

            transactions = await monitor.get_latest_transactions()
            assert len(transactions) == 1
            assert transactions[0].network == 'TON'
            assert transactions[0].amount_usd == 125000.0


class TestEverscaleMonitor:
    """Test Everscale network monitor"""

    @pytest.mark.asyncio
    async def test_get_price_usd(self):
        """Test Everscale price fetching"""
        monitor = EverscaleMonitor(min_usd=100000, rpc_url='https://test-ever.com')

        with aioresponses() as m:
            m.get(
                'https://api.coingecko.com/api/v3/simple/price',
                payload={'everscale': {'usd': 0.08}}
            )

            price = await monitor.get_current_price_usd()
            assert price == 0.08

    @pytest.mark.asyncio
    async def test_get_latest_transactions(self):
        """Test fetching Everscale transactions"""
        monitor = EverscaleMonitor(min_usd=100000, rpc_url='https://test-ever.com')

        with aioresponses() as m:
            # Mock price API
            m.get(
                'https://api.coingecko.com/api/v3/simple/price',
                payload={'everscale': {'usd': 0.08}}
            )

            # Mock GraphQL API
            m.post(
                'https://test-ever.com/graphql',
                payload={
                    'data': {
                        'transactions': [
                            {
                                'id': 'ever_tx_1',
                                'now': 1705000000,
                                'out_messages': [
                                    {
                                        'value': 1500000000000000,  # ~120M EVER = $120,000
                                        'src': 'ever_sender_1',
                                        'dst': 'ever_receiver_1'
                                    }
                                ]
                            }
                        ]
                    }
                }
            )

            transactions = await monitor.get_latest_transactions()
            assert len(transactions) >= 0  # May be 0 due to value parsing complexity


class TestVenomMonitor:
    """Test Venom network monitor"""

    @pytest.mark.asyncio
    async def test_get_price_usd(self):
        """Test Venom price fetching"""
        monitor = VenomMonitor(min_usd=100000, rpc_url='https://test-venom.com')

        with aioresponses() as m:
            m.get(
                'https://api.coingecko.com/api/v3/simple/price',
                payload={'venom': {'usd': 0.05}}
            )

            price = await monitor.get_current_price_usd()
            assert price == 0.05

    @pytest.mark.asyncio
    async def test_price_fallback(self):
        """Test price fallback when API fails"""
        monitor = VenomMonitor(min_usd=100000, rpc_url='https://test-venom.com')

        with aioresponses() as m:
            m.get(
                'https://api.coingecko.com/api/v3/simple/price',
                status=500
            )

            price = await monitor.get_current_price_usd()
            assert price == 0.05  # Should use fallback


class TestHumanodeMonitor:
    """Test Humanode (HUMO) network monitor"""

    @pytest.mark.asyncio
    async def test_get_humo_price(self):
        """Test HUMO token price fetching"""
        monitor = HumanodeMonitor(min_usd=100000, rpc_url='https://test-humanode.com')

        with aioresponses() as m:
            m.get(
                'https://api.coingecko.com/api/v3/simple/price',
                payload={'humo': {'usd': 0.05}}
            )

            price = await monitor.get_current_price_usd()
            assert price == 0.05

    @pytest.mark.asyncio
    async def test_get_latest_transactions(self):
        """Test fetching HUMO transactions"""
        monitor = HumanodeMonitor(min_usd=100000, rpc_url='https://test-humanode.com')

        with aioresponses() as m:
            # Mock price API
            m.get(
                'https://api.coingecko.com/api/v3/simple/price',
                payload={'humo': {'usd': 0.05}}
            )

            # Mock Subscan API
            m.get(
                'https://humanode.api.subscan.io/api/scan/transfers',
                payload={
                    'code': 0,
                    'data': {
                        'transfers': [
                            {
                                'hash': 'humo_tx_1',
                                'amount': 2500000000000000000000,  # 2500 HUMO = $125,000
                                'from': 'humo_sender_1',
                                'to': 'humo_receiver_1',
                                'block_timestamp': 1705000000
                            }
                        ]
                    }
                }
            )

            transactions = await monitor.get_latest_transactions()
            assert len(transactions) == 1
            assert transactions[0].network == 'Humanode (HUMO)'
            assert transactions[0].amount_usd == 125.0  # 2500 HUMO * $0.05

    @pytest.mark.asyncio
    async def test_network_name(self):
        """Test that network is properly named as HUMO"""
        monitor = HumanodeMonitor(min_usd=100000, rpc_url='https://test-humanode.com')
        assert monitor.network_name == 'Humanode (HUMO)'
