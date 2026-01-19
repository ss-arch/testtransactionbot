from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Transaction:
    def __init__(self, network: str, tx_hash: str, amount_usd: float,
                 sender: str, receiver: str, timestamp: int, amount_native: float = 0):
        self.network = network
        self.tx_hash = tx_hash
        self.amount_usd = amount_usd
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp
        self.amount_native = amount_native

    def __repr__(self):
        return f"Transaction({self.network}, {self.tx_hash}, ${self.amount_usd:,.2f})"


class BaseMonitor(ABC):
    def __init__(self, network_name: str, min_usd: float):
        self.network_name = network_name
        self.min_usd = min_usd
        self.last_checked_block = None
        self.processed_txs = set()  # Track processed transaction hashes

    @abstractmethod
    async def get_latest_transactions(self) -> List[Transaction]:
        """
        Fetch latest transactions from the network.
        Returns list of Transaction objects that exceed min_usd threshold.
        """
        pass

    @abstractmethod
    async def get_current_price_usd(self) -> float:
        """Get current token price in USD"""
        pass

    def is_duplicate(self, tx_hash: str) -> bool:
        """Check if transaction has already been processed"""
        if tx_hash in self.processed_txs:
            return True
        self.processed_txs.add(tx_hash)

        # Keep only last 1000 transactions to avoid memory issues
        if len(self.processed_txs) > 1000:
            self.processed_txs = set(list(self.processed_txs)[-1000:])

        return False

    async def fetch_and_filter(self) -> List[Transaction]:
        """Fetch transactions and filter duplicates"""
        try:
            transactions = await self.get_latest_transactions()
            # Filter out duplicates
            new_transactions = [tx for tx in transactions if not self.is_duplicate(tx.tx_hash)]
            if new_transactions:
                logger.info(f"{self.network_name}: Found {len(new_transactions)} new large transactions")
            return new_transactions
        except Exception as e:
            logger.error(f"{self.network_name}: Error fetching transactions: {e}")
            return []

    async def get_latest_transactions_any_amount(self, limit: int = 5) -> List[Transaction]:
        """
        Fetch latest transactions regardless of amount.
        Returns up to 'limit' most recent transactions.
        """
        # Default implementation - subclasses should override
        return []
