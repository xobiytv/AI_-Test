"""
Google Calendar OAuth2 sozlash skripti.
Birinchi marta ishlatishdan oldin shu skriptni ishga tushiring:
  python setup_google_calendar.py
"""
from services.calendar import get_calendar_service

if __name__ == "__main__":
    print("Google Calendar bilan ulanish...")
    service = get_calendar_service()
    if service:
        print("✅ Muvaffaqiyatli ulandi! token.json saqlandi.")
    else:
        print("❌ Ulanib bo'lmadi. credentials.json faylini tekshiring.")
