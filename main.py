#!/usr/bin/env python3
"""
Multi-Network Transaction Monitor Bot
Monitors TON, Everscale, Venom, and Humanode networks for large transactions
"""

import asyncio
import logging
import sys
from typing import List

import config
from telegram_bot import TelegramNotifier
from monitors import (
    TONMonitor,
    EverscaleMonitor,
    VenomMonitor,
    BaseMonitor,
    Transaction
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)


class TransactionMonitorBot:
    def __init__(self):
        # Validate configuration
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env file")

        self.notifier = TelegramNotifier(
            bot_token=config.TELEGRAM_BOT_TOKEN,
            chat_id=config.TELEGRAM_CHAT_ID
        )

        # Initialize monitors with network-specific token thresholds
        self.monitors: List[BaseMonitor] = [
            TONMonitor(min_tokens=config.NETWORK_THRESHOLDS['TON']),
            EverscaleMonitor(min_tokens=config.NETWORK_THRESHOLDS['Everscale']),
            VenomMonitor(min_tokens=config.NETWORK_THRESHOLDS['Venom'])
        ]

        self.is_running = False

    async def start(self):
        """Start the monitoring bot"""
        logger.info("Starting Transaction Monitor Bot...")
        logger.info(f"Poll interval: {config.POLL_INTERVAL_SECONDS} seconds")
        logger.info(f"Network thresholds: {config.NETWORK_THRESHOLDS}")

        # Send startup notification
        await self.notifier.send_startup_message()

        self.is_running = True
        await self.monitor_loop()

    async def monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Fetch transactions from all monitors concurrently
                tasks = [monitor.fetch_and_filter() for monitor in self.monitors]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Monitor error: {result}")
                        continue

                    # Send notifications for each transaction
                    for tx in result:
                        await self.notifier.send_transaction_alert(tx)
                        # Small delay between notifications to avoid rate limiting
                        await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await self.notifier.send_error_message(str(e))

            # Wait before next poll
            await asyncio.sleep(config.POLL_INTERVAL_SECONDS)

    async def stop(self):
        """Stop the monitoring bot"""
        logger.info("Stopping Transaction Monitor Bot...")
        self.is_running = False


async def main():
    """Main entry point"""
    bot = TransactionMonitorBot()

    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        await bot.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
