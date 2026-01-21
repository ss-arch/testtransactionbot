#!/usr/bin/env python3
"""
Multi-Network Transaction Monitor Bot
Monitors TON, Everscale, Venom networks for large transactions
"""

import asyncio
import logging
import sys
from typing import List

import config
from telegram.ext import Application
from telegram_bot import TelegramNotifier, setup_handlers, get_user_manager
from monitors import (
    TONMonitor,
    EverscaleMonitor,
    VenomMonitor,
    BaseMonitor,
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
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env file")

        self.notifier = TelegramNotifier(
            bot_token=config.TELEGRAM_BOT_TOKEN,
            chat_id=config.TELEGRAM_CHAT_ID
        )

        # Initialize monitors (fetch all transactions, filter per-user)
        self.monitors: List[BaseMonitor] = [
            TONMonitor(min_tokens=0),
            EverscaleMonitor(min_tokens=0),
            VenomMonitor(min_tokens=0)
        ]

        self.is_running = False
        self.application = None

    async def start(self):
        """Start the monitoring bot with command handlers"""
        logger.info("Starting Transaction Monitor Bot...")
        logger.info(f"Poll interval: {config.POLL_INTERVAL_SECONDS} seconds")
        logger.info(f"Default thresholds: {config.NETWORK_THRESHOLDS}")

        # Build application with command handlers
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        setup_handlers(self.application)

        # Initialize application
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)

        # Send startup notification to admin
        await self.notifier.send_startup_message()

        self.is_running = True
        await self.monitor_loop()

    async def monitor_loop(self):
        """Main monitoring loop"""
        user_manager = get_user_manager()

        while self.is_running:
            try:
                # Fetch transactions from all networks
                all_transactions = {}
                for monitor in self.monitors:
                    try:
                        transactions = await monitor.get_latest_transactions()
                        # Filter new transactions (not seen before)
                        new_txs = monitor.filter_new_transactions(transactions)
                        if new_txs:
                            all_transactions[monitor.network_name] = new_txs
                            logger.info(f"{monitor.network_name}: Found {len(new_txs)} new transactions")
                    except Exception as e:
                        logger.error(f"{monitor.network_name} error: {e}")

                # Send alerts to each active user based on their thresholds
                active_users = user_manager.get_active_users()
                for user in active_users:
                    for network, txs in all_transactions.items():
                        threshold = user.thresholds.get(network, 0)
                        # Filter transactions by user's threshold
                        user_txs = [tx for tx in txs if tx.amount_native >= threshold]
                        for tx in user_txs:
                            await self.notifier.send_transaction_alert_to_user(tx, user.chat_id)
                            await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await self.notifier.send_error_message(str(e))

            await asyncio.sleep(config.POLL_INTERVAL_SECONDS)

    async def stop(self):
        """Stop the monitoring bot"""
        logger.info("Stopping Transaction Monitor Bot...")
        self.is_running = False
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()


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
