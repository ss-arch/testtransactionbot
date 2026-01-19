import aiohttp
from typing import List
import logging
from .base_monitor import BaseMonitor, Transaction
import time

logger = logging.getLogger(__name__)


class TONMonitor(BaseMonitor):
    def __init__(self, min_usd: float, api_key: str = ''):
        super().__init__('TON', min_usd)
        # Use public tonscan.org API - no authentication needed
        self.api_url = 'https://toncenter.com/api/v2'
        self.price_cache = {'price': 0, 'timestamp': 0}

    async def get_current_price_usd(self) -> float:
        """Get TON price in USD from CoinGecko (public API)"""
        # Cache price for 5 minutes
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
        """Fetch latest TON transactions from public API"""
        transactions = []
        try:
            ton_price = await self.get_current_price_usd()
            if ton_price == 0:
                logger.warning("TON: Cannot fetch transactions without price data")
                return []

            async with aiohttp.ClientSession() as session:
                # Get latest masterchain blocks to find recent transactions
                async with session.get(
                    f'{self.api_url}/getMasterchainInfo'
                ) as response:
                    if response.status != 200:
                        logger.warning(f"TON: API returned status {response.status}")
                        return []

                    masterchain_data = await response.json()
                    if not masterchain_data.get('ok'):
                        return []

                    last_block = masterchain_data['result']['last']
                    seqno = last_block['seqno']

                    # Get transactions from recent blocks
                    for block_offset in range(10):  # Check last 10 blocks
                        current_seqno = seqno - block_offset

                        try:
                            async with session.get(
                                f'{self.api_url}/getBlockTransactions',
                                params={
                                    'workchain': -1,
                                    'shard': '-9223372036854775808',
                                    'seqno': current_seqno
                                }
                            ) as block_response:
                                if block_response.status != 200:
                                    continue

                                block_data = await block_response.json()
                                if not block_data.get('ok'):
                                    continue

                                block_txs = block_data['result']['transactions']

                                for tx_info in block_txs[:20]:  # Limit to 20 transactions per block
                                    try:
                                        # Get detailed transaction info
                                        async with session.get(
                                            f'{self.api_url}/getTransactions',
                                            params={
                                                'address': tx_info['account'],
                                                'limit': 1,
                                                'lt': tx_info['lt'],
                                                'hash': tx_info['hash']
                                            }
                                        ) as tx_response:
                                            if tx_response.status != 200:
                                                continue

                                            tx_data = await tx_response.json()
                                            if not tx_data.get('ok') or not tx_data.get('result'):
                                                continue

                                            tx = tx_data['result'][0]

                                            # Parse transaction value
                                            if tx.get('out_msgs'):
                                                for out_msg in tx['out_msgs']:
                                                    value_nano = int(out_msg.get('value', 0))
                                                    value_ton = value_nano / 1e9
                                                    value_usd = value_ton * ton_price

                                                    if value_usd >= self.min_usd:
                                                        tx_hash = tx.get('transaction_id', {}).get('hash', 'Unknown')
                                                        sender = out_msg.get('source', 'Unknown')
                                                        receiver = out_msg.get('destination', 'Unknown')
                                                        timestamp = tx.get('utime', 0)

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
                                        logger.debug(f"TON: Error parsing transaction details: {e}")
                                        continue

                        except Exception as e:
                            logger.debug(f"TON: Error fetching block {current_seqno}: {e}")
                            continue

        except Exception as e:
            logger.error(f"TON: Error fetching transactions: {e}")

        logger.info(f"TON: Found {len(transactions)} transactions above ${self.min_usd}")
        return transactions

    async def get_latest_transactions_any_amount(self, limit: int = 5) -> List[Transaction]:
        """Fetch latest TON transactions regardless of amount"""
        transactions = []
        try:
            ton_price = await self.get_current_price_usd()
            if ton_price == 0:
                return []

            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.api_url}/getMasterchainInfo') as response:
                    if response.status != 200:
                        return []

                    masterchain_data = await response.json()
                    if not masterchain_data.get('ok'):
                        return []

                    last_block = masterchain_data['result']['last']
                    seqno = last_block['seqno']

                    for block_offset in range(5):
                        if len(transactions) >= limit:
                            break

                        current_seqno = seqno - block_offset

                        try:
                            async with session.get(
                                f'{self.api_url}/getBlockTransactions',
                                params={'workchain': -1, 'shard': '-9223372036854775808', 'seqno': current_seqno}
                            ) as block_response:
                                if block_response.status != 200:
                                    continue

                                block_data = await block_response.json()
                                if not block_data.get('ok'):
                                    continue

                                block_txs = block_data['result']['transactions']

                                for tx_info in block_txs[:10]:
                                    if len(transactions) >= limit:
                                        break

                                    try:
                                        async with session.get(
                                            f'{self.api_url}/getTransactions',
                                            params={'address': tx_info['account'], 'limit': 1, 'lt': tx_info['lt'], 'hash': tx_info['hash']}
                                        ) as tx_response:
                                            if tx_response.status != 200:
                                                continue

                                            tx_data = await tx_response.json()
                                            if not tx_data.get('ok') or not tx_data.get('result'):
                                                continue

                                            tx = tx_data['result'][0]

                                            if tx.get('out_msgs'):
                                                for out_msg in tx['out_msgs']:
                                                    if len(transactions) >= limit:
                                                        break

                                                    value_nano = int(out_msg.get('value', 0))
                                                    if value_nano == 0:
                                                        continue

                                                    value_ton = value_nano / 1e9
                                                    value_usd = value_ton * ton_price

                                                    tx_hash = tx.get('transaction_id', {}).get('hash', 'Unknown')
                                                    sender = out_msg.get('source', 'Unknown')
                                                    receiver = out_msg.get('destination', 'Unknown')
                                                    timestamp = tx.get('utime', 0)

                                                    transactions.append(Transaction(
                                                        network='TON',
                                                        tx_hash=tx_hash,
                                                        amount_usd=value_usd,
                                                        sender=sender,
                                                        receiver=receiver,
                                                        timestamp=timestamp,
                                                        amount_native=value_ton
                                                    ))

                                    except Exception:
                                        continue

                        except Exception:
                            continue

        except Exception as e:
            logger.debug(f"TON: Error fetching dashboard transactions: {e}")

        return transactions[:limit]
