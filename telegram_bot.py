import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from datetime import datetime
from monitors import Transaction
import config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    def format_transaction_message(self, tx: Transaction) -> str:
        """Format transaction details into a readable message"""
        # Format timestamp
        dt = datetime.fromtimestamp(tx.timestamp)
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')

        # Format addresses (shorten for readability)
        sender_short = self._shorten_address(tx.sender)
        receiver_short = self._shorten_address(tx.receiver)

        # Get explorer URL
        explorer_info = config.EXPLORERS.get(tx.network, {})
        explorer_link = f"{explorer_info.get('tx', '')}{tx.tx_hash}"

        # Build message
        message = f"""
🚨 <b>Large Transaction Detected!</b>

💰 <b>Amount:</b> ${tx.amount_usd:,.2f}
   ({tx.amount_native:,.4f} {self._get_token_symbol(tx.network)})

🌐 <b>Network:</b> {tx.network}

📤 <b>From:</b> <code>{sender_short}</code>
📥 <b>To:</b> <code>{receiver_short}</code>

🔗 <b>Transaction:</b> <code>{self._shorten_hash(tx.tx_hash)}</code>

🕒 <b>Time:</b> {time_str}

🔍 <a href="{explorer_link}">View on Explorer</a>
"""
        return message.strip()

    def _shorten_address(self, address: str) -> str:
        """Shorten address for display"""
        if len(address) > 16:
            return f"{address[:8]}...{address[-8:]}"
        return address

    def _shorten_hash(self, tx_hash: str) -> str:
        """Shorten transaction hash for display"""
        if len(tx_hash) > 16:
            return f"{tx_hash[:12]}...{tx_hash[-12:]}"
        return tx_hash

    def _get_token_symbol(self, network: str) -> str:
        """Get token symbol for network"""
        symbols = {
            'TON': 'TON',
            'Everscale': 'EVER',
            'Venom': 'VENOM'
        }
        return symbols.get(network, 'TOKEN')

    async def send_transaction_alert(self, tx: Transaction):
        """Send transaction alert to Telegram"""
        try:
            message = self.format_transaction_message(tx)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            logger.info(f"Sent alert for {tx.network} transaction: {tx.tx_hash}")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")

    async def send_startup_message(self):
        """Send bot startup notification"""
        try:
            message = f"""
🤖 <b>Transaction Monitor Bot Started</b>

Monitoring networks: TON, Everscale, Venom
Alert threshold: ${config.MIN_TRANSACTION_USD:,.0f}
Poll interval: {config.POLL_INTERVAL_SECONDS}s

✅ Bot is now active and monitoring...
"""
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message.strip(),
                parse_mode='HTML'
            )
            logger.info("Sent startup message")
        except Exception as e:
            logger.error(f"Failed to send startup message: {e}")

    async def send_error_message(self, error_msg: str):
        """Send error notification"""
        try:
            message = f"⚠️ <b>Error:</b> {error_msg}"
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    async def send_dashboard(self, network_transactions: dict):
        """Send dashboard with last 5 transactions per network"""
        try:
            message = "📊 <b>Transaction Dashboard</b>\n\n"

            for network, transactions in network_transactions.items():
                token_symbol = self._get_token_symbol(network)
                message += f"<b>{network}</b>\n"

                if not transactions:
                    message += "  No recent transactions\n\n"
                    continue

                for tx in transactions[:5]:
                    explorer_info = config.EXPLORERS.get(network, {})
                    tx_link = f"{explorer_info.get('tx', '')}{tx.tx_hash}"
                    amount_str = f"{tx.amount_native:,.4f} {token_symbol}"
                    message += f"  • <a href=\"{tx_link}\">{amount_str}</a>\n"

                message += "\n"

            dt = datetime.now()
            message += f"🕒 Updated: {dt.strftime('%H:%M:%S')}"

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message.strip(),
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            logger.info("Sent dashboard update")
        except Exception as e:
            logger.error(f"Failed to send dashboard: {e}")
