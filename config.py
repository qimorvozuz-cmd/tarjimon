import os

# Bot tokenini Railway'da Variables bo'limiga BOT_TOKEN nomi bilan qo'shing.
# Local test uchun quyidagi qatorga o'zingizning tokeningizni yozishingiz mumkin.
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")

# Claude (Anthropic) API kaliti - yuqori sifatli tarjima uchun.
# Railway'da Variables bo'limiga ANTHROPIC_API_KEY nomi bilan qo'shing.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "PUT_YOUR_ANTHROPIC_KEY_HERE")

# Tarjima uchun ishlatiladigan model
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# Admin(lar) Telegram ID raqami(lari). Bir nechta bo'lsa vergul bilan ajrating: "111,222"
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

# Ma'lumotlar bazasi fayli
DB_PATH = os.getenv("DB_PATH", "data/users.db")

# Bir vaqtda tarjima qilinadigan matn uzunligi chegarasi (Telegram xabar limiti ~4096)
MAX_TEXT_LEN = 4000

# Hujjat tarjima uchun ruxsat etilgan fayl kengaytmalari
ALLOWED_DOC_EXT = (".pdf", ".docx", ".txt")

# Qo'llab-quvvatlanadigan tillar: {kod: (bayroq, nom)}
LANGUAGES = {
    "uz": ("🇺🇿", "O'zbek"),
    "ru": ("🇷🇺", "Rus"),
    "en": ("🇬🇧", "Ingliz"),
    "tr": ("🇹🇷", "Turk"),
    "kk": ("🇰🇿", "Qozoq"),
    "tg": ("🇹🇯", "Tojik"),
    "ky": ("🇰🇬", "Qirg'iz"),
    "ar": ("🇸🇦", "Arab"),
    "zh-CN": ("🇨🇳", "Xitoy"),
    "de": ("🇩🇪", "Nemis"),
    "fr": ("🇫🇷", "Fransuz"),
    "es": ("🇪🇸", "Ispan"),
    "it": ("🇮🇹", "Italyan"),
    "ja": ("🇯🇵", "Yapon"),
    "ko": ("🇰🇷", "Koreys"),
    "hi": ("🇮🇳", "Hind"),
    "fa": ("🇮🇷", "Fors"),
    "az": ("🇦🇿", "Ozarbayjon"),
}

# Claude'ga prompt yozishda ishlatiladigan til nomlari (o'sha tilning o'zida emas,
# universal tushunish uchun inglizcha nomlar qo'llaniladi)
LANG_NAMES_EN = {
    "uz": "Uzbek",
    "ru": "Russian",
    "en": "English",
    "tr": "Turkish",
    "kk": "Kazakh",
    "tg": "Tajik",
    "ky": "Kyrgyz",
    "ar": "Arabic",
    "zh-CN": "Chinese",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "hi": "Hindi",
    "fa": "Persian",
    "az": "Azerbaijani",
}
