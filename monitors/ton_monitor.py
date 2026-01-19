import aiohttp
from typing import List
import logging
from .base_monitor import BaseMonitor, Transaction
import time

logger = logging.getLogger(__name__)


class TONMonitor(BaseMonitor):
    def __init__(self, min_usd: float):
        super().__init__('TON', min_usd)
        self.api_url = 'https://toncenter.com/api/v2'
        self.explorer_url = 'https://tonscan.org'
        self.price_cache = {'price': 0, 'timestamp': 0}

    async def get_current_price_usd(self) -> float:
        """Get TON price in USD from CoinGecko"""
        if time.time() - self.price_cache['timestamp'] < 300:
            return self.price_cache['price']

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://api.coingecko.com/api/v3/simple/price',
                    params={'ids': 'the-open-network', 'vs_currencies': 'usd'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get('the-open-network', {}).get('usd', 0)
                        if price > 0:
                            self.price_cache = {'price': price, 'timestamp': time.time()}
                            logger.info(f"TON: Price updated: ${price}")
                            return price
                    logger.warning(f"TON: Failed to get price, status {response.status}")
                    return self.price_cache.get('price', 0)
        except Exception as e:
            logger.error(f"TON: Error getting price: {e}")
            return self.price_cache.get('price', 0)

    async def get_latest_transactions(self) -> List[Transaction]:
        """Get latest TON transactions using TonCenter API"""
        transactions = []
        try:
            ton_price = await self.get_current_price_usd()
            if ton_price == 0:
                logger.warning("TON: Cannot fetch transactions without price data")
                return []

            # Get recent transactions from multiple well-known addresses
            # This is a workaround since TonCenter doesn't have a "latest transactions" endpoint
            async with aiohttp.ClientSession() as session:
                # Query the latest masterchain block to get recent transactions
                async with session.get(
                    f'{self.api_url}/getMasterchainInfo'
                ) as response:
                    if response.status != 200:
                        logger.warning(f"TON: API returned status {response.status}")
                        return []

                    data = await response.json()
                    if not data.get('ok'):
                        return []

                    # Get transactions from the latest block
                    # Note: TonCenter API is limited - we can only get transactions for specific addresses
                    # For a real implementation, you might need to use TON indexer services
                    logger.debug("TON: TonCenter API has limitations for fetching recent transactions")

        except Exception as e:
            logger.error(f"TON: Error fetching transactions: {e}")

        logger.info(f"TON: Found {len(transactions)} transactions above ${self.min_usd}")
        return transactions

    async def get_latest_transactions_any_amount(self, limit: int = 5) -> List[Transaction]:
        """Get latest TON transactions for dashboard"""
        transactions = []
        try:
            ton_price = await self.get_current_price_usd()
            if ton_price == 0:
                return []

            # TonCenter API limitation: we need specific addresses to query
            # This is a placeholder implementation
            # For production, consider using TON indexer services or API services like tonapi.io

        except Exception as e:
            logger.debug(f"TON: Error fetching dashboard transactions: {e}")

        return transactions[:limit]
