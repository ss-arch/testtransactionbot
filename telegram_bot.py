import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
from datetime import datetime
from monitors import Transaction
import config

logger = logging.getLogger(__name__)

# Runtime thresholds (can be changed via commands)
runtime_thresholds = dict(config.NETWORK_THRESHOLDS)


def get_threshold(network: str) -> float:
    """Get current threshold for network"""
    return runtime_thresholds.get(network, 0)


def set_threshold(network: str, value: float) -> bool:
    """Set threshold for network"""
    if network in runtime_thresholds:
        runtime_thresholds[network] = value
        return True
    return False


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.bot_token = bot_token

    def format_transaction_message(self, tx: Transaction) -> str:
        """Format transaction details into a readable message"""
        dt = datetime.fromtimestamp(tx.timestamp)
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')

        sender_short = self._shorten_address(tx.sender)
        receiver_short = self._shorten_address(tx.receiver)

        explorer_info = config.EXPLORERS.get(tx.network, {})
        explorer_link = f"{explorer_info.get('tx', '')}{tx.tx_hash}"

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
        if len(address) > 16:
            return f"{address[:8]}...{address[-8:]}"
        return address

    def _shorten_hash(self, tx_hash: str) -> str:
        if len(tx_hash) > 16:
            return f"{tx_hash[:12]}...{tx_hash[-12:]}"
        return tx_hash

    def _get_token_symbol(self, network: str) -> str:
        symbols = {
            'TON': 'TON',
            'Everscale': 'EVER',
            'Venom': 'VENOM'
        }
        return symbols.get(network, 'TOKEN')

    async def send_transaction_alert(self, tx: Transaction):
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
        try:
            thresholds = '\n'.join([
                f"  • {network}: {threshold:,.0f} tokens"
                for network, threshold in runtime_thresholds.items()
            ])
            message = f"""
🤖 <b>Transaction Monitor Bot Started</b>

Monitoring networks: TON, Everscale, Venom
Token thresholds:
{thresholds}

Commands:
/thresholds - view current thresholds
/threshold [network] [value] - set threshold

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
        try:
            message = f"⚠️ <b>Error:</b> {error_msg}"
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")


async def thresholds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current thresholds"""
    thresholds = '\n'.join([
        f"  • {network}: {threshold:,.0f} tokens"
        for network, threshold in runtime_thresholds.items()
    ])
    message = f"""
📊 <b>Current Thresholds</b>

{thresholds}

To change: /threshold [network] [value]
Example: /threshold TON 5000
"""
    await update.message.reply_text(message.strip(), parse_mode='HTML')


async def threshold_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set threshold for a network"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /threshold [network] [value]\n"
            "Networks: TON, Everscale, Venom\n"
            "Example: /threshold TON 5000"
        )
        return

    network = context.args[0]
    network_map = {
        'ton': 'TON',
        'everscale': 'Everscale',
        'ever': 'Everscale',
        'venom': 'Venom'
    }
    network = network_map.get(network.lower(), network)

    try:
        value = float(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid value. Please enter a number.")
        return

    if value < 0:
        await update.message.reply_text("Threshold must be a positive number.")
        return

    if set_threshold(network, value):
        await update.message.reply_text(
            f"✅ {network} threshold set to {value:,.0f} tokens",
            parse_mode='HTML'
        )
        logger.info(f"Threshold changed: {network} = {value}")
    else:
        await update.message.reply_text(
            f"Unknown network: {network}\n"
            "Available networks: TON, Everscale, Venom"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    message = """
🤖 <b>Transaction Monitor Bot</b>

Commands:
/thresholds - view current thresholds
/threshold [network] [value] - set threshold
/help - show this message

Networks: TON, Everscale, Venom

Example:
/threshold TON 5000
/threshold Everscale 50000
"""
    await update.message.reply_text(message.strip(), parse_mode='HTML')


def setup_handlers(application: Application):
    """Setup command handlers"""
    application.add_handler(CommandHandler("thresholds", thresholds_command))
    application.add_handler(CommandHandler("threshold", threshold_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", help_command))
