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
        return f"Transaction({self.network}, {self.tx_hash}, {self.amount_native:,.2f} tokens)"


class BaseMonitor(ABC):
    def __init__(self, network_name: str, min_tokens: float):
        self.network_name = network_name
        self.min_tokens = min_tokens
        self.last_checked_block = None
        self.processed_txs = set()  # Track processed transaction hashes

    @abstractmethod
    async def get_latest_transactions() -> List[Transaction]:
        """
        Fetch latest transactions from the network.
        Returns list of Transaction objects that exceed min_tokens threshold.
        """
        pass

    @abstractmethod
    async def get_current_price_usd(self) -> float:
        """Get current token price in USD"""
        pass

    def filter_new_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """Filter out already processed transactions"""
        new_txs = []
        for tx in transactions:
            if tx.tx_hash not in self.processed_txs:
                self.processed_txs.add(tx.tx_hash)
                new_txs.append(tx)

        # Keep only last 1000 transactions to avoid memory issues
        if len(self.processed_txs) > 1000:
            self.processed_txs = set(list(self.processed_txs)[-1000:])

        return new_txs
