import aiohttp
from typing import List
import logging
from .base_monitor import BaseMonitor, Transaction
import time

logger = logging.getLogger(__name__)


class VenomMonitor(BaseMonitor):
    def __init__(self, min_usd: float, rpc_url: str):
        super().__init__('Venom', min_usd)
        self.rpc_url = rpc_url
        self.price_cache = {'price': 0, 'timestamp': 0}

    async def get_current_price_usd(self) -> float:
        """Get VENOM price in USD with caching"""
        # Cache price for 5 minutes
        if time.time() - self.price_cache['timestamp'] < 300:
            return self.price_cache['price']

        try:
            async with aiohttp.ClientSession() as session:
                # Using CoinGecko API for price
                async with session.get(
                    'https://api.coingecko.com/api/v3/simple/price',
                    params={'ids': 'venom', 'vs_currencies': 'usd'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get('venom', {}).get('usd', 0)
                        self.price_cache = {'price': price, 'timestamp': time.time()}
                        return price
                    else:
                        logger.warning(f"Venom: Failed to get price, status {response.status}")
                        # Fallback to approximate price if API fails
                        if self.price_cache['price'] == 0:
                            self.price_cache = {'price': 0.05, 'timestamp': time.time()}  # Approximate fallback
                        return self.price_cache.get('price', 0)
        except Exception as e:
            logger.error(f"Venom: Error getting price: {e}")
            if self.price_cache['price'] == 0:
                self.price_cache = {'price': 0.05, 'timestamp': time.time()}
            return self.price_cache.get('price', 0)

    async def get_latest_transactions(self) -> List[Transaction]:
        """Fetch latest Venom transactions"""
        transactions = []
        try:
            venom_price = await self.get_current_price_usd()
            if venom_price == 0:
                logger.warning("Venom: Cannot fetch transactions without price data")
                return []

            async with aiohttp.ClientSession() as session:
                # Query recent transactions using GraphQL (Venom uses similar structure to Everscale)
                query = """
                query {
                  transactions(
                    orderBy: { path: "now", direction: DESC }
                    limit: 50
                  ) {
                    id
                    now
                    balance_delta
                    account_addr
                    out_messages {
                      value
                      dst
                      src
                    }
                  }
                }
                """

                async with session.post(
                    f'{self.rpc_url}/graphql',
                    json={'query': query},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Venom: API returned status {response.status}")
                        return []

                    data = await response.json()
                    txs = data.get('data', {}).get('transactions', [])

                    for tx in txs:
                        try:
                            tx_hash = tx.get('id', '')
                            timestamp = int(tx.get('now', 0))

                            # Check out messages
                            for msg in tx.get('out_messages', []):
                                value_nano = int(msg.get('value', '0'), 16) if isinstance(msg.get('value'), str) else int(msg.get('value', 0))
                                value_venom = value_nano / 1e9
                                value_usd = value_venom * venom_price

                                if value_usd >= self.min_usd:
                                    sender = msg.get('src', 'Unknown')
                                    receiver = msg.get('dst', 'Unknown')

                                    transactions.append(Transaction(
                                        network='Venom',
                                        tx_hash=tx_hash,
                                        amount_usd=value_usd,
                                        sender=sender,
                                        receiver=receiver,
                                        timestamp=timestamp,
                                        amount_native=value_venom
                                    ))

                        except Exception as e:
                            logger.error(f"Venom: Error parsing transaction: {e}")
                            continue

        except Exception as e:
            logger.error(f"Venom: Error fetching transactions: {e}")

        return transactions
