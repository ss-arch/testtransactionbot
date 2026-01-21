import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
from datetime import datetime
from monitors import Transaction
import config

logger = logging.getLogger(__name__)


class UserSettings:
    """Settings for a single user"""
    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self.enabled = False  # Disabled by default, user must /start
        self.thresholds = dict(config.NETWORK_THRESHOLDS)


class UserManager:
    """Manages per-user settings"""
    def __init__(self):
        self.users: dict[str, UserSettings] = {}

    def get_or_create_user(self, chat_id: str) -> UserSettings:
        """Get user settings or create new user with defaults"""
        chat_id = str(chat_id)
        if chat_id not in self.users:
            self.users[chat_id] = UserSettings(chat_id)
            logger.info(f"New user registered: {chat_id}")
        return self.users[chat_id]

    def get_user(self, chat_id: str) -> UserSettings | None:
        """Get user settings if exists"""
        return self.users.get(str(chat_id))

    def get_active_users(self) -> list[UserSettings]:
        """Get all users with monitoring enabled"""
        return [u for u in self.users.values() if u.enabled]

    def get_all_users(self) -> list[UserSettings]:
        """Get all registered users"""
        return list(self.users.values())


# Global user manager
user_manager = UserManager()


def get_user_manager() -> UserManager:
    """Get the global user manager"""
    return user_manager


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

        exchange_line = f"\n🏦 <b>Exchange:</b> {tx.exchange_name}" if tx.exchange_name else ""

        message = f"""
🚨 <b>Exchange Transaction Detected!</b>

💰 <b>Amount:</b> ${tx.amount_usd:,.2f}
   ({tx.amount_native:,.4f} {self._get_token_symbol(tx.network)})

🌐 <b>Network:</b> {tx.network}{exchange_line}

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

    async def send_transaction_alert_to_user(self, tx: Transaction, chat_id: str):
        """Send transaction alert to specific user"""
        try:
            message = self.format_transaction_message(tx)
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            logger.info(f"Sent alert for {tx.network} transaction to {chat_id}: {tx.tx_hash}")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message to {chat_id}: {e}")

    async def send_startup_message(self):
        """Send bot startup notification to admin"""
        try:
            message = f"""
🤖 <b>Transaction Monitor Bot Started</b>

Monitoring networks: TON, Everscale, Venom
Default thresholds: {config.NETWORK_THRESHOLDS}

Bot is ready to accept users.
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
        """Send error notification to admin"""
        try:
            message = f"⚠️ <b>Error:</b> {error_msg}"
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start monitoring for user"""
    chat_id = str(update.effective_chat.id)
    user = user_manager.get_or_create_user(chat_id)
    user.enabled = True

    thresholds = '\n'.join([
        f"  • {network}: {threshold:,.0f} tokens"
        for network, threshold in user.thresholds.items()
    ])
    message = f"""
🤖 <b>Transaction Monitor Bot</b>

✅ Monitoring started!

<b>Networks:</b> TON, Everscale, Venom

<b>Your thresholds:</b>
{thresholds}

<b>Commands:</b>
/start - start monitoring
/stop - stop monitoring
/status - show your status
/thresholds - view your thresholds
/threshold [network] [value] - set threshold
/help - show this message

<b>Example:</b>
/threshold TON 5000
/threshold Everscale 50000
"""
    await update.message.reply_text(message.strip(), parse_mode='HTML')
    logger.info(f"User {chat_id} started monitoring")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop monitoring for user"""
    chat_id = str(update.effective_chat.id)
    user = user_manager.get_or_create_user(chat_id)
    user.enabled = False

    message = """
⏹ <b>Monitoring Stopped</b>

No alerts will be sent until you use /start again.
"""
    await update.message.reply_text(message.strip(), parse_mode='HTML')
    logger.info(f"User {chat_id} stopped monitoring")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status for user"""
    chat_id = str(update.effective_chat.id)
    user = user_manager.get_or_create_user(chat_id)

    status = "🟢 Active" if user.enabled else "🔴 Stopped"
    thresholds = '\n'.join([
        f"  • {network}: {threshold:,.0f} tokens"
        for network, threshold in user.thresholds.items()
    ])
    message = f"""
📊 <b>Your Status</b>

Status: {status}

Your thresholds:
{thresholds}
"""
    await update.message.reply_text(message.strip(), parse_mode='HTML')


async def thresholds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current thresholds for user"""
    chat_id = str(update.effective_chat.id)
    user = user_manager.get_or_create_user(chat_id)

    thresholds = '\n'.join([
        f"  • {network}: {threshold:,.0f} tokens"
        for network, threshold in user.thresholds.items()
    ])
    message = f"""
📊 <b>Your Thresholds</b>

{thresholds}

To change: /threshold [network] [value]
Example: /threshold TON 5000
"""
    await update.message.reply_text(message.strip(), parse_mode='HTML')


async def threshold_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set threshold for user"""
    chat_id = str(update.effective_chat.id)
    user = user_manager.get_or_create_user(chat_id)

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

    if network in user.thresholds:
        user.thresholds[network] = value
        await update.message.reply_text(
            f"✅ Your {network} threshold set to {value:,.0f} tokens",
            parse_mode='HTML'
        )
        logger.info(f"User {chat_id} set {network} threshold to {value}")
    else:
        await update.message.reply_text(
            f"Unknown network: {network}\n"
            "Available networks: TON, Everscale, Venom"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    message = """
🤖 <b>Transaction Monitor Bot</b>

Monitor large transactions on TON, Everscale, and Venom networks.

Commands:
/start - start monitoring
/stop - stop monitoring
/status - show your status
/thresholds - view your thresholds
/threshold [network] [value] - set threshold
/help - show this message

Networks: TON, Everscale, Venom

Example:
/threshold TON 5000
/threshold Everscale 50000

Each user has independent settings.
"""
    await update.message.reply_text(message.strip(), parse_mode='HTML')


def setup_handlers(application: Application):
    """Setup command handlers"""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("thresholds", thresholds_command))
    application.add_handler(CommandHandler("threshold", threshold_command))
    application.add_handler(CommandHandler("help", help_command))
