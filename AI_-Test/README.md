# 🤖 Shaxsiy AI Assistant (Telegram Bot)

Ovozli xabarlar orqali boshqariladigan shaxsiy AI assistant.

## Imkoniyatlar

- 🎤 Ovozli xabardan vazifa/xarajatni avtomatik ajratish
- 📅 Google Kalendariga avtomatik qo'shish
- ⏰ Telegram orqali eslatmalar (15 daqiqa oldin)
- 💰 Kunlik xarajatlarni kuzatish
- 📊 Kun oxirida samaradorlik hisoboti (22:00)

## Vazifa kategoriyalari

1. 📚 Shaxsiy rivojlanish
2. 💼 Loyihalar
3. 🤝 Kunlik uchrashuvlar
4. ✨ Yaxshi amallar

## O'rnatish

### 1. Kerakli kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 2. .env faylini sozlash

```bash
cp .env.example .env
```

`.env` faylini oching va quyidagilarni to'ldiring:

```
TELEGRAM_BOT_TOKEN=    # @BotFather dan olingan token
OPENAI_API_KEY=        # OpenAI API kaliti
ADMIN_CHAT_ID=         # Sizning Telegram chat ID (@userinfobot orqali bilib oling)
```

### 3. Google Calendar sozlash

1. [Google Cloud Console](https://console.cloud.google.com) ga kiring
2. Yangi loyiha yarating
3. Google Calendar API ni yoqing
4. OAuth 2.0 credentials yarating (Desktop app)
5. `credentials.json` faylini yuklab oling va loyiha papkasiga qo'ying
6. Birinchi marta sozlash uchun:

```bash
python setup_google_calendar.py
```

### 4. Botni ishga tushirish

```bash
python bot.py
```

## Buyruqlar

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni boshlash |
| `/today` | Bugungi vazifalar ro'yxati |
| `/expenses` | Bugungi xarajatlar |
| `/report` | Hozir hisobot ko'rish |
| `/add_expense 50000 Tushlik` | Xarajat qo'shish |

## Foydalanish

Ovozli xabar yuboring, masalan:
- *"Bugun soat 15da Ahmad bilan uchrashuv bor"*
- *"Ertaga 10:00 da kitob o'qish"*
- *"Tushlikka 45000 so'm sarfladim"*

Bot avtomatik tushunadi va saqlaydi!
