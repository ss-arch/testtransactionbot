import aiohttp
from typing import List
import logging
from .base_monitor import BaseMonitor, Transaction
import time
import config

logger = logging.getLogger(__name__)


class TONMonitor(BaseMonitor):
    def __init__(self, min_tokens: float):
        super().__init__('TON', min_tokens)
        self.api_url = 'https://toncenter.com/api/v3'
        self.explorer_url = 'https://tonscan.org'
        self.price_cache = {'price': 0, 'timestamp': 0}
        self.elector_addresses = config.ELECTOR_ADDRESSES.get('TON', [])

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

    def _nano_to_ton(self, nano_value: str) -> float:
        """Convert nano TON to TON"""
        try:
            if not nano_value:
                return 0
            return int(nano_value) / 1_000_000_000
        except Exception as e:
            logger.debug(f"TON: Error converting nano value {nano_value}: {e}")
            return 0

    def _format_address(self, address: str) -> str:
        """Format TON address for display"""
        if not address:
            return 'Unknown'
        if ':' in address:
            return address
        return address[:16] + '...' if len(address) > 16 else address

    def _is_elector_transaction(self, sender: str, receiver: str) -> bool:
        """Check if transaction involves elector contract"""
        for elector_addr in self.elector_addresses:
            if sender and elector_addr in sender:
                return True
            if receiver and elector_addr in receiver:
                return True
        return False

    async def get_latest_transactions(self) -> List[Transaction]:
        """Get latest TON transactions using TonCenter API v3"""
        transactions = []
        try:
            ton_price = await self.get_current_price_usd()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_url}/transactions',
                    params={'limit': 50, 'sort': 'desc'}
                ) as response:
                    if response.status != 200:
                        logger.warning(f"TON: API returned status {response.status}")
                        return []

                    data = await response.json()
                    tx_list = data.get('transactions', [])

                    for tx in tx_list:
                        try:
                            in_msg = tx.get('in_msg')
                            if not in_msg or not in_msg.get('value'):
                                continue

                            amount_ton = self._nano_to_ton(in_msg['value'])
                            if amount_ton == 0:
                                continue

                            sender = in_msg.get('source', 'Unknown')
                            receiver = in_msg.get('destination', 'Unknown')

                            # Skip elector transactions
                            if self._is_elector_transaction(sender, receiver):
                                logger.debug(f"TON: Skipping elector transaction {tx['hash']}")
                                continue

                            amount_usd = amount_ton * ton_price if ton_price > 0 else 0

                            transactions.append(Transaction(
                                network='TON',
                                tx_hash=tx['hash'],
                                amount_usd=amount_usd,
                                sender=self._format_address(sender),
                                receiver=self._format_address(receiver),
                                timestamp=tx['now'],
                                amount_native=amount_ton
                            ))

                        except Exception as e:
                            logger.debug(f"TON: Error parsing transaction: {e}")
                            continue

        except Exception as e:
            logger.error(f"TON: Error fetching transactions: {e}")

        return transactions
