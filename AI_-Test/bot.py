import asyncio
import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from services.database import init_db
from services.scheduler import setup_scheduler
from handlers.commands import (
    cmd_start,
    cmd_today,
    cmd_expenses,
    cmd_report,
    cmd_add_expense,
    callback_confirm,
)
from handlers.voice import handle_voice, handle_voice_callback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(app: Application):
    await init_db()
    setup_scheduler(app)
    logger.info("Bot ishga tushdi ✅")


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN .env faylida ko'rsatilmagan!")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("expenses", cmd_expenses))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("add_expense", cmd_add_expense))

    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.add_handler(CallbackQueryHandler(handle_voice_callback, pattern="^(save_task:|save_expense:|discard)"))
    app.add_handler(CallbackQueryHandler(callback_confirm, pattern="^(confirm_task:|cancel)"))

    logger.info("Bot polling boshlandi...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
