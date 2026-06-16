from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import DAILY_REPORT_HOUR, DAILY_REPORT_MINUTE, ADMIN_CHAT_ID, TIMEZONE

scheduler = AsyncIOScheduler(timezone=TIMEZONE)
_bot_app = None


def setup_scheduler(app):
    global _bot_app
    _bot_app = app

    scheduler.add_job(
        _check_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="reminder_check",
        replace_existing=True,
    )

    scheduler.add_job(
        _send_daily_reports,
        trigger=CronTrigger(hour=DAILY_REPORT_HOUR, minute=DAILY_REPORT_MINUTE, timezone=TIMEZONE),
        id="daily_report",
        replace_existing=True,
    )

    scheduler.start()


async def _check_reminders():
    if not _bot_app:
        return

    from services.database import get_upcoming_unreminded_tasks, mark_reminded
    from config import CATEGORIES

    tasks = await get_upcoming_unreminded_tasks()
    for task in tasks:
        try:
            cat_name = CATEGORIES.get(task.category, "Vazifa")
            time_str = task.scheduled_at.strftime("%H:%M") if task.scheduled_at else ""
            text = (
                f"⏰ *Eslatma!*\n\n"
                f"📌 {task.title}\n"
                f"🗂 {cat_name}\n"
                f"🕐 Vaqt: {time_str}\n"
            )
            if task.description:
                text += f"📝 {task.description}"

            await _bot_app.bot.send_message(
                chat_id=task.chat_id,
                text=text,
                parse_mode="Markdown",
            )
            await mark_reminded(task.id)
        except Exception as e:
            print(f"Reminder error for task {task.id}: {e}")


async def _send_daily_reports():
    if not _bot_app:
        return

    from services.database import get_today_tasks, get_today_expenses, get_all_chat_ids
    from services.ai import generate_daily_report

    chat_ids = await get_all_chat_ids()
    if ADMIN_CHAT_ID and ADMIN_CHAT_ID not in chat_ids:
        chat_ids.append(ADMIN_CHAT_ID)

    for chat_id in chat_ids:
        try:
            tasks = await get_today_tasks(chat_id)
            expenses = await get_today_expenses(chat_id)
            report = await generate_daily_report(tasks, expenses)
            await _bot_app.bot.send_message(
                chat_id=chat_id,
                text=report,
                parse_mode="Markdown",
            )
        except Exception as e:
            print(f"Daily report error for {chat_id}: {e}")
