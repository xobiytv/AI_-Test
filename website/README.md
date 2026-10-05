# Tog' Safari — Biznestown Biznes Club

"Tog' Safari — yetakchi tadbirkorlar bilan!" tadbiri uchun bir sahifali sayt (24–25 oktyabr 2026, Refzomin Resort, Zomin).

## Ishga tushirish
Build kerak emas — `index.html` ni brauzerda oching yoki `website/` papkasini istalgan statik hostingga (Netlify, Vercel, GitHub Pages, cPanel) yuklang.

Lokal ko'rish: `cd website && python3 -m http.server 8000` → http://localhost:8000

## Tahrirlash kerak bo'lgan joylar
- `index.html` — telefon raqam (`+998 (00) 000-00-00`) va Telegram (`@biznestown`) — haqiqiylariga almashtiring.
- `script.js` → `CONFIG`:
  - `eventDate` — teskari sanoq uchun sana.
  - `formEndpoint` — arizalar tushadigan URL (Google Apps Script, Formspree va h.k.). Bo'sh bo'lsa, ariza tayyor matn bilan Telegramda ochiladi.
  - `telegramUsername` — arizalar boradigan Telegram akkaunt.
- `assets/` — rasmlar afishalardan kesib olingan. Mehmonxonaning haqiqiy rasmlari bilan almashtirish tavsiya etiladi.
