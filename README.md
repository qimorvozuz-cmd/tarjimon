# 🌍 AI Translator Bot (Telegram)

O'zbek, rus, ingliz va yana 15+ tilda ishlaydigan tarjimon bot. Aiogram 3.22 asosida yozilgan.

## Imkoniyatlari

- 📝 **Text tarjima** — istalgan matnni yuboring, Claude AI orqali yuqori sifatli tarjima qilinadi
- 🖼 **Rasm tarjima** — rasm ichidagi matnni OCR orqali o'qib, Claude orqali tarjima qiladi
- 📄 **Hujjat tarjima** — PDF, DOCX, TXT fayllarni tarjima qilib, yangi .docx qaytaradi
- ⚙️ **Til sozlamalari** — har bir foydalanuvchi o'z tarjima yo'nalishini tanlaydi
- 🕘 **Tarix** — foydalanuvchi o'z tarjimalari tarixini ko'ra oladi
- 👨‍💼 **Admin panel** — `/stats` statistika, `/broadcast` orqali barcha foydalanuvchilarga xabar

## Loyiha tuzilishi

```
TranslatorBot/
├── bot.py                 # Botni ishga tushiruvchi asosiy fayl
├── config.py               # Token, admin ID, tillar ro'yxati
├── database.py              # SQLite bilan ishlash
├── requirements.txt
├── Procfile                 # Railway uchun
├── nixpacks.toml             # Railway'da tesseract-ocr o'rnatish uchun
├── handlers/
│   ├── start.py             # /start, til tanlash, yordam
│   ├── text.py               # Matn tarjimasi
│   ├── image.py               # Rasm (OCR) tarjimasi
│   ├── document.py             # Hujjat tarjimasi
│   └── admin.py                # Admin buyruqlari
├── keyboards/
│   ├── menu.py                  # Asosiy menyu
│   └── languages.py              # Til tanlash tugmalari
└── services/
    ├── translate.py               # Claude API orqali tarjima
    ├── ocr.py                      # pytesseract orqali OCR
    └── document.py                  # PDF/DOCX/TXT o'qish va yozish
```

## O'rnatish (local test uchun)

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Windows/Mac/Linux'da OCR ishlashi uchun Tesseract OCR dasturini alohida o'rnatish kerak:
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Ubuntu/Debian: `sudo apt install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng`
- Mac: `brew install tesseract`

`config.py` faylida `BOT_TOKEN` va `ANTHROPIC_API_KEY` ni o'zingizning ma'lumotlaringizga almashtiring
(yoki `BOT_TOKEN` / `ANTHROPIC_API_KEY` environment variable orqali bering), so'ng:

```bash
python bot.py
```

## Railway'ga joylashtirish

1. Ushbu loyihani GitHub repo qilib yuklang.
2. Railway'da **New Project → Deploy from GitHub repo** tanlang.
3. **Variables** bo'limiga qo'shing:
   - `BOT_TOKEN` — BotFather'dan olingan token
   - `ANTHROPIC_API_KEY` — Claude API kalitingiz (console.anthropic.com)
   - `ADMIN_IDS` — sizning Telegram ID raqamingiz (bir nechta bo'lsa vergul bilan)
   - (ixtiyoriy) `CLAUDE_MODEL` — standart holatda `claude-sonnet-4-6` ishlatiladi
4. Railway `nixpacks.toml` fayli orqali avtomatik Tesseract OCR va til paketlarini o'rnatadi.
5. Deploy tugagach, bot avtomatik ishga tushadi (`Procfile` — `worker: python bot.py`).

## Muhim eslatmalar

- Tarjima **Claude API** orqali amalga oshiriladi — kontekstni tushunadi, tabiiy va aniq tarjima beradi. Har bir so'rov ozgina xarajat talab qiladi (Anthropic hisobingizdan).
- OCR sifat jihatidan aniq va tekis matnli rasmlarda yaxshi ishlaydi; qiyshiq/xira rasmlarda aniqlik pasayishi mumkin.
- Skanerlangan (rasmga aylantirilgan) PDF fayllardan matn to'g'ridan-to'g'ri o'qilmaydi — bunday holatda avval rasm sifatida yuborib OCR qildirish tavsiya etiladi.
- O'zbek tili uchun Tesseract'ning "uzb" til paketi ba'zi tizimlarda mavjud emas — bunday holda bot avtomatik inglizcha OCR'ga o'tadi (`services/ocr.py` dagi fallback).

## Kengaytirish g'oyalari

- Voice (ovozli xabar) tarjimasi — `speech_recognition` + matn tarjima orqali
- Referal tizimi — `database.py` ga `referrals` jadvali qo'shish
- Inline mode — istalgan chatda `@BotUsername matn` yozib tez tarjima qilish
