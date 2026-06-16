from telegram import Update
from telegram.ext import ContextTypes

from config import CATEGORIES
from services.database import (
    get_today_tasks,
    get_today_expenses,
    save_expense,
    mark_completed,
)
from services.ai import generate_daily_report
from models import Expense
from datetime import datetime


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Assalomu alaykum!*\n\n"
        "Men sizning shaxsiy AI assistantingizman. Quyidagilarni qila olaman:\n\n"
        "🎤 *Ovozli xabar* yuboring — vazifa yoki xarajatni avtomatik belgilayman\n"
        "📅 Google Kalendaringizga voqealar qo'shaman\n"
        "⏰ Vaqti kelganda eslatma yuboraman\n"
        "📊 Kunlik hisobot tayyorlayman\n\n"
        "*Buyruqlar:*\n"
        "/today — Bugungi vazifalar\n"
        "/expenses — Bugungi xarajatlar\n"
        "/report — Hozir hisobot ko'rish\n"
        "/add\\_expense — Xarajat qo'shish\n\n"
        "💡 *Masalan:* \"Bugun soat 15da Ahmad bilan uchrashuv bor\" deb ovozli xabar yuboring!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tasks = await get_today_tasks(chat_id)

    if not tasks:
        await update.message.reply_text("📭 Bugun hech qanday vazifa yo'q.")
        return

    lines = ["📋 *BUGUNGI VAZIFALAR*\n"]
    for cat_id, cat_name in CATEGORIES.items():
        cat_tasks = [t for t in tasks if t.category == cat_id]
        if not cat_tasks:
            continue
        lines.append(f"\n{cat_name}:")
        for t in cat_tasks:
            status = "✅" if t.completed else "⬜"
            time_str = t.scheduled_at.strftime(" (%H:%M)") if t.scheduled_at else ""
            lines.append(f"  {status} {t.title}{time_str}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    expenses = await get_today_expenses(chat_id)

    if not expenses:
        await update.message.reply_text("💰 Bugun xarajat kiritilmagan.")
        return

    total_uzs = sum(e.amount for e in expenses if e.currency == "UZS")
    total_usd = sum(e.amount for e in expenses if e.currency == "USD")

    lines = ["💰 *BUGUNGI XARAJATLAR*\n"]
    for e in expenses:
        lines.append(f"• {e.description}: *{e.amount:,.0f} {e.currency}*")

    if total_uzs > 0:
        lines.append(f"\n💵 Jami UZS: *{total_uzs:,.0f}*")
    if total_usd > 0:
        lines.append(f"💵 Jami USD: *{total_usd:.2f}*")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("⏳ Hisobot tayyorlanmoqda...")

    tasks = await get_today_tasks(chat_id)
    expenses = await get_today_expenses(chat_id)
    report = await generate_daily_report(tasks, expenses)

    await update.message.reply_text(report, parse_mode="Markdown")


async def cmd_add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /add_expense 50000 Tushlik"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ Format: `/add_expense <summa> <tavsif>`\n"
            "Misol: `/add_expense 50000 Tushlik`",
            parse_mode="Markdown",
        )
        return

    try:
        amount_str = context.args[0].replace(",", "").replace(".", "")
        amount = float(amount_str)
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri summa. Misol: `50000`", parse_mode="Markdown")
        return

    currency = "UZS"
    if amount < 1000 and "usd" in " ".join(context.args).lower():
        currency = "USD"

    description = " ".join(context.args[1:])
    expense = Expense(
        chat_id=update.effective_chat.id,
        amount=amount,
        currency=currency,
        description=description,
        created_at=datetime.now(),
    )
    await save_expense(expense)
    await update.message.reply_text(
        f"✅ Xarajat saqlandi!\n💰 {description}: *{amount:,.0f} {currency}*",
        parse_mode="Markdown",
    )


async def callback_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat_id

    if data.startswith("confirm_task:"):
        task_id = int(data.split(":")[1])
        await mark_completed(task_id)
        await query.edit_message_text(
            query.message.text + "\n\n✅ *Bajarildi!*", parse_mode="Markdown"
        )
    elif data == "cancel":
        await query.edit_message_text("❌ Bekor qilindi.")
