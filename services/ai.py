import json
import os
from datetime import datetime
from typing import Optional

from openai import AsyncOpenAI

from config import OPENAI_API_KEY, TIMEZONE
from models import ParsedVoice

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def transcribe_voice(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="uz",
        )
    return response.text


async def parse_transcript(transcript: str) -> ParsedVoice:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    system_prompt = f"""Siz Uzbek tilidagi ovozli xabarlarni tahlil qiluvchi AI assistantsiz.
Hozirgi vaqt: {now} (vaqt zonasi: {TIMEZONE})

Foydalanuvchi xabarini tahlil qiling va quyidagi JSON formatida qaytaring:

Agar bu VAZIFA/UCHRASHIV bo'lsa:
{{
  "type": "task",
  "title": "vazifa sarlavhasi",
  "description": "qo'shimcha ma'lumot",
  "category": 1,  // 1=Shaxsiy rivojlanish, 2=Loyihalar, 3=Kunlik uchrashuvlar, 4=Yaxshi amallar
  "scheduled_at": "2024-01-15 14:30"  // yoki null
}}

Agar bu XARAJAT bo'lsa:
{{
  "type": "expense",
  "amount": 50000,
  "currency": "UZS",  // yoki "USD"
  "expense_description": "nima uchun sarflandi"
}}

Agar noaniq bo'lsa:
{{
  "type": "unknown"
}}

Kategoriyalarni aniqlash:
- 1 (Shaxsiy rivojlanish): kitob o'qish, sport, kurs, o'rganish, mashq
- 2 (Loyihalar): ish, kod, meeting, loyiha, vazifa, topshiriq
- 3 (Kunlik uchrashuvlar): uchrashuv, qo'ng'iroq, call, suhbat, doktor, bank
- 4 (Yaxshi amallar): sadaqa, yordam, namoz, xayr, ehson

Faqat JSON qaytaring, boshqa hech narsa yozmang."""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    data = json.loads(response.choices[0].message.content)
    result = ParsedVoice(type=data.get("type", "unknown"), transcript=transcript)

    if result.type == "task":
        result.title = data.get("title", "")
        result.description = data.get("description", "")
        result.category = int(data.get("category", 1))
        raw_dt = data.get("scheduled_at")
        if raw_dt:
            try:
                result.scheduled_at = datetime.strptime(raw_dt, "%Y-%m-%d %H:%M")
            except ValueError:
                result.scheduled_at = None
    elif result.type == "expense":
        result.amount = float(data.get("amount", 0))
        result.currency = data.get("currency", "UZS")
        result.expense_description = data.get("expense_description", "")

    return result


async def generate_daily_report(tasks, expenses) -> str:
    from config import CATEGORIES

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.completed)
    effectiveness = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)

    category_stats = {}
    for cat_id, cat_name in CATEGORIES.items():
        cat_tasks = [t for t in tasks if t.category == cat_id]
        cat_done = sum(1 for t in cat_tasks if t.completed)
        if cat_tasks:
            category_stats[cat_name] = f"{cat_done}/{len(cat_tasks)}"

    total_uzs = sum(e.amount for e in expenses if e.currency == "UZS")
    total_usd = sum(e.amount for e in expenses if e.currency == "USD")

    expense_lines = ""
    if expenses:
        lines = [f"  • {e.description}: {e.amount:,.0f} {e.currency}" for e in expenses]
        expense_lines = "\n".join(lines)
    else:
        expense_lines = "  Bugun xarajat yo'q"

    cat_lines = "\n".join(
        f"  {name}: {stat}" for name, stat in category_stats.items()
    ) or "  Vazifalar yo'q"

    emoji = "🔥" if effectiveness >= 80 else "👍" if effectiveness >= 50 else "💪"

    prompt = f"""Foydalanuvchiga bugungi kunning qisqa motivatsion xulosasini yozing (2-3 gap, o'zbek tilida).
Samaradorlik: {effectiveness}%. Bajarilgan vazifalar: {completed_tasks}/{total_tasks}.
Agar samaradorlik yuqori bo'lsa - maqtang, past bo'lsa - ertaga yaxshi harakat qilishga undang."""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.7,
    )
    motivation = response.choices[0].message.content.strip()

    report = f"""📊 *KUNLIK HISOBOT*

{emoji} *Samaradorlik: {effectiveness}%*
✅ Bajarildi: {completed_tasks}/{total_tasks} vazifa

📋 *Kategoriyalar bo'yicha:*
{cat_lines}

💰 *Bugungi xarajatlar:*
{expense_lines}"""

    if total_uzs > 0:
        report += f"\n  💵 Jami UZS: {total_uzs:,.0f}"
    if total_usd > 0:
        report += f"\n  💵 Jami USD: {total_usd:.2f}"

    report += f"\n\n💬 {motivation}"
    return report
