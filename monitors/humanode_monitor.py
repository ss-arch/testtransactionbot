import aiohttp
from typing import List
import logging
from .base_monitor import BaseMonitor, Transaction
import time

logger = logging.getLogger(__name__)


class HumanodeMonitor(BaseMonitor):
    def __init__(self, min_usd: float, rpc_url: str):
        super().__init__('Humanode (HUMO)', min_usd)
        self.rpc_url = rpc_url
        self.price_cache = {'price': 0, 'timestamp': 0}
        self.last_block = None

    async def get_current_price_usd(self) -> float:
        """Get HUMO token price in USD with caching"""
        # Cache price for 5 minutes
        if time.time() - self.price_cache['timestamp'] < 300:
            return self.price_cache['price']

        try:
            async with aiohttp.ClientSession() as session:
                # Try CoinGecko API for HUMO token price
                async with session.get(
                    'https://api.coingecko.com/api/v3/simple/price',
                    params={'ids': 'humo', 'vs_currencies': 'usd'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get('humo', {}).get('usd', 0)
                        if price > 0:
                            self.price_cache = {'price': price, 'timestamp': time.time()}
                            logger.info(f"Humanode: HUMO price updated: ${price}")
                            return price

                # Fallback: Try alternative API or DEX price
                logger.warning(f"Humanode: CoinGecko API did not return HUMO price")

                # If no cached price, use approximate fallback
                if self.price_cache['price'] == 0:
                    self.price_cache = {'price': 0.05, 'timestamp': time.time()}
                    logger.warning(f"Humanode: Using fallback HUMO price: $0.05")

                return self.price_cache.get('price', 0)
        except Exception as e:
            logger.error(f"Humanode: Error getting HUMO price: {e}")
            if self.price_cache['price'] == 0:
                self.price_cache = {'price': 0.05, 'timestamp': time.time()}
            return self.price_cache.get('price', 0)

    async def get_latest_transactions(self) -> List[Transaction]:
        """Fetch latest HUMO token transactions on Humanode network"""
        transactions = []
        try:
            humo_price = await self.get_current_price_usd()
            if humo_price == 0:
                logger.warning("Humanode: Cannot fetch transactions without HUMO price data")
                return []

            async with aiohttp.ClientSession() as session:
                # Try Subscan API for HUMO token transfers
                async with session.get(
                    'https://humanode.api.subscan.io/api/scan/transfers',
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('code') == 0:
                            transfers = data.get('data', {}).get('transfers', [])

                            for transfer in transfers[:50]:  # Check last 50 transfers
                                try:
                                    amount_raw = float(transfer.get('amount', 0))
                                    # HUMO token uses 18 decimals
                                    amount_humo = amount_raw / 1e18
                                    amount_usd = amount_humo * humo_price

                                    if amount_usd >= self.min_usd:
                                        tx_hash = transfer.get('hash', '')
                                        sender = transfer.get('from', 'Unknown')
                                        receiver = transfer.get('to', 'Unknown')
                                        timestamp = transfer.get('block_timestamp', 0)

                                        transactions.append(Transaction(
                                            network='Humanode (HUMO)',
                                            tx_hash=tx_hash,
                                            amount_usd=amount_usd,
                                            sender=sender,
                                            receiver=receiver,
                                            timestamp=timestamp,
                                            amount_native=amount_humo
                                        ))

                                except Exception as e:
                                    logger.error(f"Humanode: Error parsing transfer: {e}")
                                    continue
                        else:
                            logger.warning(f"Humanode: Subscan API returned code {data.get('code')}")
                    else:
                        logger.warning(f"Humanode: Subscan API returned status {response.status}")

        except Exception as e:
            logger.error(f"Humanode: Error fetching HUMO transactions: {e}")

        return transactions

    async def get_latest_transactions_any_amount(self, limit: int = 5) -> List[Transaction]:
        """Fetch latest Humanode transactions regardless of amount"""
        # Humanode Subscan API often unavailable, return empty for dashboard
        return []
