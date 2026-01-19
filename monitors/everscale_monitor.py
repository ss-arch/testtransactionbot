import aiohttp
from typing import List
import logging
from .base_monitor import BaseMonitor, Transaction
import time
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class EverscaleMonitor(BaseMonitor):
    def __init__(self, min_usd: float):
        super().__init__('Everscale', min_usd)
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

    async def get_latest_transactions(self) -> List[Transaction]:
        """Scrape latest Everscale transactions from everscan.io"""
        transactions = []
        try:
            ever_price = await self.get_current_price_usd()
            if ever_price == 0:
                logger.warning("Everscale: Cannot fetch transactions without price data")
                return []

            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.explorer_url}/') as response:
                    if response.status != 200:
                        logger.warning(f"Everscale: Explorer returned status {response.status}")
                        return []

                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')

                    # Scrape transaction table
                    tx_rows = soup.find_all('tr', class_='transaction-row')[:20]

                    for row in tx_rows:
                        try:
                            tx_link = row.find('a', href=lambda x: x and '/transactions/' in x)
                            if not tx_link:
                                continue
                            tx_hash = tx_link['href'].split('/')[-1]

                            amount_cell = row.find('td', class_='amount')
                            if not amount_cell:
                                continue
                            amount_text = amount_cell.get_text(strip=True)
                            amount_ever = float(amount_text.replace('EVER', '').replace(',', '').strip())

                            amount_usd = amount_ever * ever_price

                            if amount_usd >= self.min_usd:
                                address_cells = row.find_all('td', class_='address')
                                sender = address_cells[0].get_text(strip=True) if len(address_cells) > 0 else 'Unknown'
                                receiver = address_cells[1].get_text(strip=True) if len(address_cells) > 1 else 'Unknown'

                                timestamp = int(time.time())

                                transactions.append(Transaction(
                                    network='Everscale',
                                    tx_hash=tx_hash,
                                    amount_usd=amount_usd,
                                    sender=sender,
                                    receiver=receiver,
                                    timestamp=timestamp,
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
        """Scrape latest Everscale transactions regardless of amount"""
        transactions = []
        try:
            ever_price = await self.get_current_price_usd()
            if ever_price == 0:
                return []

            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.explorer_url}/') as response:
                    if response.status != 200:
                        return []

                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')

                    tx_rows = soup.find_all('tr', class_='transaction-row')[:limit]

                    for row in tx_rows:
                        try:
                            tx_link = row.find('a', href=lambda x: x and '/transactions/' in x)
                            if not tx_link:
                                continue
                            tx_hash = tx_link['href'].split('/')[-1]

                            amount_cell = row.find('td', class_='amount')
                            if not amount_cell:
                                continue
                            amount_text = amount_cell.get_text(strip=True)
                            amount_ever = float(amount_text.replace('EVER', '').replace(',', '').strip())

                            amount_usd = amount_ever * ever_price

                            address_cells = row.find_all('td', class_='address')
                            sender = address_cells[0].get_text(strip=True) if len(address_cells) > 0 else 'Unknown'
                            receiver = address_cells[1].get_text(strip=True) if len(address_cells) > 1 else 'Unknown'

                            timestamp = int(time.time())

                            transactions.append(Transaction(
                                network='Everscale',
                                tx_hash=tx_hash,
                                amount_usd=amount_usd,
                                sender=sender,
                                receiver=receiver,
                                timestamp=timestamp,
                                amount_native=amount_ever
                            ))

                        except Exception:
                            continue

        except Exception as e:
            logger.debug(f"Everscale: Error fetching dashboard transactions: {e}")

        return transactions[:limit]
