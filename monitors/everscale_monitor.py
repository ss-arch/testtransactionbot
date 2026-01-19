import aiohttp
from typing import List
import logging
from .base_monitor import BaseMonitor, Transaction
import time

logger = logging.getLogger(__name__)


class EverscaleMonitor(BaseMonitor):
    def __init__(self, min_usd: float):
        super().__init__('Everscale', min_usd)
        self.graphql_url = 'https://mainnet.evercloud.dev/89a3b8f46e484c2a8afc86f1fac08ccb/graphql'
        self.explorer_url = 'https://everscan.io'
        self.price_cache = {'price': 0, 'timestamp': 0}

    async def get_current_price_usd(self) -> float:
        """Get EVER price in USD from CoinGecko"""
        if time.time() - self.price_cache['timestamp'] < 300:
            return self.price_cache['price']

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://api.coingecko.com/api/v3/simple/price',
                    params={'ids': 'everscale', 'vs_currencies': 'usd'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get('everscale', {}).get('usd', 0)
                        if price > 0:
                            self.price_cache = {'price': price, 'timestamp': time.time()}
                            logger.info(f"Everscale: Price updated: ${price}")
                            return price
                    logger.warning(f"Everscale: Failed to get price, status {response.status}")
                    return self.price_cache.get('price', 0)
        except Exception as e:
            logger.error(f"Everscale: Error getting price: {e}")
            return self.price_cache.get('price', 0)

    def _hex_to_decimal(self, hex_value: str) -> float:
        """Convert hex value to decimal and divide by 10^9 for EVER"""
        if not hex_value or hex_value == "0x0":
            return 0
        try:
            value_nano = int(hex_value, 16)
            return value_nano / 1_000_000_000  # Convert from nanoEVER to EVER
        except Exception as e:
            logger.debug(f"Everscale: Error converting hex {hex_value}: {e}")
            return 0

    async def get_latest_transactions(self) -> List[Transaction]:
        """Get latest Everscale transactions using GraphQL API"""
        transactions = []
        try:
            ever_price = await self.get_current_price_usd()
            if ever_price == 0:
                logger.warning("Everscale: Cannot fetch transactions without price data")
                return []

            query = """
            query {
                transactions(
                    limit: 50,
                    orderBy: {path: "now", direction: DESC}
                ) {
                    id
                    now
                    balance_delta
                    account_addr
                    in_message {
                        value
                        src
                        dst
                    }
                }
            }
            """

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.graphql_url,
                    json={'query': query},
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Everscale: GraphQL API returned status {response.status}")
                        return []

                    data = await response.json()
                    tx_list = data.get('data', {}).get('transactions', [])

                    for tx in tx_list:
                        try:
                            in_msg = tx.get('in_message')
                            if not in_msg or not in_msg.get('value'):
                                continue

                            # Convert hex value to EVER
                            amount_ever = self._hex_to_decimal(in_msg['value'])
                            if amount_ever == 0:
                                continue

                            amount_usd = amount_ever * ever_price

                            if amount_usd >= self.min_usd:
                                transactions.append(Transaction(
                                    network='Everscale',
                                    tx_hash=tx['id'],
                                    amount_usd=amount_usd,
                                    sender=in_msg.get('src', 'Unknown'),
                                    receiver=in_msg.get('dst', 'Unknown'),
                                    timestamp=tx['now'],
                                    amount_native=amount_ever
                                ))

                        except Exception as e:
                            logger.debug(f"Everscale: Error parsing transaction: {e}")
                            continue

        except Exception as e:
            logger.error(f"Everscale: Error fetching transactions: {e}")

        logger.info(f"Everscale: Found {len(transactions)} transactions above ${self.min_usd}")
        return transactions

    async def get_latest_transactions_any_amount(self, limit: int = 5) -> List[Transaction]:
        """Get latest Everscale transactions for dashboard, extending search up to 5 minutes"""
        transactions = []
        try:
            ever_price = await self.get_current_price_usd()
            if ever_price == 0:
                return []

            current_time = int(time.time())
            min_time = current_time - 300  # 5 minutes ago

            # Fetch more transactions to ensure we have enough within time range
            query = """
            query {
                transactions(
                    limit: 100,
                    orderBy: {path: "now", direction: DESC}
                ) {
                    id
                    now
                    balance_delta
                    account_addr
                    in_message {
                        value
                        src
                        dst
                    }
                }
            }
            """

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.graphql_url,
                    json={'query': query},
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status != 200:
                        return []

                    data = await response.json()
                    tx_list = data.get('data', {}).get('transactions', [])

                    for tx in tx_list:
                        try:
                            # Stop if we have enough transactions
                            if len(transactions) >= limit:
                                break

                            # Skip transactions older than 5 minutes
                            if tx['now'] < min_time:
                                continue

                            in_msg = tx.get('in_message')
                            if not in_msg or not in_msg.get('value'):
                                # Use balance_delta if no in_message
                                amount_ever = self._hex_to_decimal(tx.get('balance_delta', '0x0'))
                                if amount_ever <= 0:
                                    continue
                                sender = 'Unknown'
                                receiver = tx.get('account_addr', 'Unknown')
                            else:
                                amount_ever = self._hex_to_decimal(in_msg['value'])
                                sender = in_msg.get('src', 'Unknown')
                                receiver = in_msg.get('dst', 'Unknown')

                            if amount_ever == 0:
                                continue

                            amount_usd = amount_ever * ever_price

                            transactions.append(Transaction(
                                network='Everscale',
                                tx_hash=tx['id'],
                                amount_usd=amount_usd,
                                sender=sender,
                                receiver=receiver,
                                timestamp=tx['now'],
                                amount_native=amount_ever
                            ))

                        except Exception:
                            continue

        except Exception as e:
            logger.debug(f"Everscale: Error fetching dashboard transactions: {e}")

        return transactions[:limit]
