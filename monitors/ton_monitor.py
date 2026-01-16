import aiohttp
from typing import List
import logging
from .base_monitor import BaseMonitor, Transaction
import time

logger = logging.getLogger(__name__)


class TONMonitor(BaseMonitor):
    def __init__(self, min_usd: float, api_key: str = ''):
        super().__init__('TON', min_usd)
        self.api_key = api_key
        self.api_url = 'https://tonapi.io/v2'
        self.price_cache = {'price': 0, 'timestamp': 0}

    async def get_current_price_usd(self) -> float:
        """Get TON price in USD with caching"""
        # Cache price for 5 minutes
        if time.time() - self.price_cache['timestamp'] < 300:
            return self.price_cache['price']

        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
                async with session.get(
                    f'{self.api_url}/rates?tokens=ton&currencies=usd',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data['rates']['TON']['prices']['USD']
                        self.price_cache = {'price': price, 'timestamp': time.time()}
                        return price
                    else:
                        logger.warning(f"TON: Failed to get price, status {response.status}")
                        return self.price_cache.get('price', 0)
        except Exception as e:
            logger.error(f"TON: Error getting price: {e}")
            return self.price_cache.get('price', 0)

    async def get_latest_transactions(self) -> List[Transaction]:
        """Fetch latest TON transactions"""
        transactions = []
        try:
            ton_price = await self.get_current_price_usd()
            if ton_price == 0:
                logger.warning("TON: Cannot fetch transactions without price data")
                return []

            # Calculate minimum TON amount needed
            min_ton = self.min_usd / ton_price

            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}

                # Get latest transactions from blockchain
                async with session.get(
                    f'{self.api_url}/blockchain/transactions',
                    headers=headers,
                    params={'limit': 100}
                ) as response:
                    if response.status != 200:
                        logger.warning(f"TON: API returned status {response.status}")
                        return []

                    data = await response.json()

                    for tx in data.get('transactions', []):
                        try:
                            # Extract transaction details
                            tx_hash = tx.get('hash', '')
                            timestamp = tx.get('utime', 0)

                            # Get transaction value
                            out_msgs = tx.get('out_msgs', [])
                            in_msg = tx.get('in_msg', {})

                            # Check outgoing messages
                            for msg in out_msgs:
                                value_nano = int(msg.get('value', 0))
                                value_ton = value_nano / 1e9
                                value_usd = value_ton * ton_price

                                if value_usd >= self.min_usd:
                                    sender = msg.get('source', {}).get('address', 'Unknown')
                                    receiver = msg.get('destination', {}).get('address', 'Unknown')

                                    transactions.append(Transaction(
                                        network='TON',
                                        tx_hash=tx_hash,
                                        amount_usd=value_usd,
                                        sender=sender,
                                        receiver=receiver,
                                        timestamp=timestamp,
                                        amount_native=value_ton
                                    ))

                            # Check incoming message
                            if in_msg:
                                value_nano = int(in_msg.get('value', 0))
                                value_ton = value_nano / 1e9
                                value_usd = value_ton * ton_price

                                if value_usd >= self.min_usd:
                                    sender = in_msg.get('source', {}).get('address', 'Unknown')
                                    receiver = in_msg.get('destination', {}).get('address', 'Unknown')

                                    transactions.append(Transaction(
                                        network='TON',
                                        tx_hash=tx_hash,
                                        amount_usd=value_usd,
                                        sender=sender,
                                        receiver=receiver,
                                        timestamp=timestamp,
                                        amount_native=value_ton
                                    ))

                        except Exception as e:
                            logger.error(f"TON: Error parsing transaction: {e}")
                            continue

        except Exception as e:
            logger.error(f"TON: Error fetching transactions: {e}")

        return transactions
