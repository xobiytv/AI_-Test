import os
import tempfile
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import CATEGORIES
from models import Task, Expense, ParsedVoice
from services.ai import transcribe_voice, parse_transcript
from services.database import save_task, save_expense
from services.calendar import create_calendar_event

# Store pending parsed results: chat_id -> ParsedVoice
_pending: dict[int, ParsedVoice] = {}


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🎤 Ovozli xabar qabul qilindi, tahlil qilinmoqda...")

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await file.download_to_drive(tmp_path)
        transcript = await transcribe_voice(tmp_path)
    finally:
        os.unlink(tmp_path)

    await msg.edit_text(f'📝 *Transkript:*\n"{transcript}"\n\n🔍 Tahlil qilinmoqda...', parse_mode="Markdown")

    parsed = await parse_transcript(transcript)
    chat_id = update.effective_chat.id
    _pending[chat_id] = parsed

    if parsed.type == "task":
        cat_name = CATEGORIES.get(parsed.category, "Noma'lum")
        time_str = parsed.scheduled_at.strftime("%d.%m.%Y %H:%M") if parsed.scheduled_at else "Belgilanmagan"

        text = (
            f"✅ *Vazifa aniqlandi:*\n\n"
            f"📌 *Sarlavha:* {parsed.title}\n"
            f"🗂 *Kategoriya:* {cat_name}\n"
            f"🕐 *Vaqt:* {time_str}\n"
        )
        if parsed.description:
            text += f"📝 *Tavsif:* {parsed.description}\n"

        text += "\nSaqlansinmi?"
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Ha, saqlash", callback_data=f"save_task:{chat_id}"),
                InlineKeyboardButton("❌ Yo'q", callback_data="discard"),
            ]
        ])
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

    elif parsed.type == "expense":
        text = (
            f"💰 *Xarajat aniqlandi:*\n\n"
            f"💵 *Summa:* {parsed.amount:,.0f} {parsed.currency}\n"
            f"📝 *Tavsif:* {parsed.expense_description}\n\n"
            f"Saqlansinmi?"
        )
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Ha, saqlash", callback_data=f"save_expense:{chat_id}"),
                InlineKeyboardButton("❌ Yo'q", callback_data="discard"),
            ]
        ])
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

    else:
        await msg.edit_text(
            f'❓ *Nima demoqchi ekanligingizni tushunmadim.*\n\n'
            f'Transkript: "{transcript}"\n\n'
            f'Iltimos, vazifa yoki xarajat haqida gapirib bering.',
            parse_mode="Markdown",
        )
        _pending.pop(chat_id, None)


async def handle_voice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "discard":
        chat_id = query.message.chat_id
        _pending.pop(chat_id, None)
        await query.edit_message_text("❌ Bekor qilindi.")
        return

    if data.startswith("save_task:"):
        chat_id = int(data.split(":")[1])
        parsed = _pending.pop(chat_id, None)
        if not parsed:
            await query.edit_message_text("⚠️ Ma'lumot topilmadi. Qaytadan yuboring.")
            return

        task = Task(
            chat_id=chat_id,
            title=parsed.title,
            description=parsed.description,
            category=parsed.category,
            scheduled_at=parsed.scheduled_at,
            created_at=datetime.now(),
        )

        calendar_event_id = None
        if parsed.scheduled_at:
            calendar_event_id = await create_calendar_event(
                title=parsed.title,
                description=parsed.description,
                start_dt=parsed.scheduled_at,
            )
        task.calendar_event_id = calendar_event_id

        task_id = await save_task(task)

        cat_name = CATEGORIES.get(parsed.category, "")
        cal_status = "📅 Google Kalendariga qo'shildi ✅" if calendar_event_id else "📅 Kalendar: ulanmagan"
        time_str = parsed.scheduled_at.strftime("%d.%m.%Y %H:%M") if parsed.scheduled_at else "—"

        await query.edit_message_text(
            f"✅ *Vazifa saqlandi!*\n\n"
            f"📌 {parsed.title}\n"
            f"🗂 {cat_name}\n"
            f"🕐 {time_str}\n"
            f"{cal_status}",
            parse_mode="Markdown",
        )

    elif data.startswith("save_expense:"):
        chat_id = int(data.split(":")[1])
        parsed = _pending.pop(chat_id, None)
        if not parsed:
            await query.edit_message_text("⚠️ Ma'lumot topilmadi. Qaytadan yuboring.")
            return

        expense = Expense(
            chat_id=chat_id,
            amount=parsed.amount,
            currency=parsed.currency,
            description=parsed.expense_description,
            created_at=datetime.now(),
        )
        await save_expense(expense)

        await query.edit_message_text(
            f"✅ *Xarajat saqlandi!*\n\n"
            f"💰 {parsed.expense_description}: *{parsed.amount:,.0f} {parsed.currency}*",
            parse_mode="Markdown",
        )
