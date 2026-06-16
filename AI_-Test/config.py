import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
DATABASE_PATH = os.getenv("DATABASE_PATH", "assistant.db")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]

CATEGORIES = {
    1: "📚 Shaxsiy rivojlanish",
    2: "💼 Loyihalar",
    3: "🤝 Kunlik uchrashuvlar",
    4: "✨ Yaxshi amallar",
}

DAILY_REPORT_HOUR = 22
DAILY_REPORT_MINUTE = 0
REMINDER_MINUTES_BEFORE = 15
