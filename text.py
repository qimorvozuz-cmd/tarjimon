from aiogram import Router, F
from aiogram.types import Message

import database as db
from config import LANGUAGES, MAX_TEXT_LEN
from keyboards.menu import MAIN_MENU_BTNS
from services.translate import translate_text

router = Router()


@router.message(F.text == MAIN_MENU_BTNS["text"])
async def text_mode_info(message: Message):
    user = db.get_user(message.from_user.id) or {}
    src = user.get("source_lang", "uz")
    tgt = user.get("target_lang", "ru")
    src_flag, src_name = LANGUAGES.get(src, ("🌐", src))
    tgt_flag, tgt_name = LANGUAGES.get(tgt, ("🌐", tgt))
    await message.answer(
        f"📝 Hozirgi yo'nalish: {src_flag} {src_name} ↔ {tgt_flag} {tgt_name}\n\n"
        "Menga istalgan matnni yuboring — men uni avtomatik tarjima qilib beraman.\n"
        "Yo'nalishni o'zgartirish uchun ⚙️ Til sozlamalari bo'limidan foydalaning."
    )


@router.message(F.text.func(lambda t: t and not t.startswith("/")))
async def auto_translate(message: Message):
    text = message.text.strip()
    if not text:
        return
    if len(text) > MAX_TEXT_LEN:
        await message.answer(f"⚠️ Matn juda uzun (max {MAX_TEXT_LEN} belgi). Hujjat sifatida yuboring.")
        return

    user = db.get_user(message.from_user.id)
    if not user:
        db.add_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name or "")
        user = db.get_user(message.from_user.id)

    src = user.get("source_lang", "uz")
    tgt = user.get("target_lang", "ru")

    # Foydalanuvchi ikki tildan birida yozadi deb faraz qilamiz:
    # agar u source_lang'da yozgan bo'lsa -> target_lang'ga,
    # aks holda (target_lang'da yozgan bo'lsa) -> source_lang'ga tarjima qilamiz.
    detected_as_target = _looks_like(text, tgt) and not _looks_like(text, src)

    if detected_as_target:
        translate_to = src
    else:
        translate_to = tgt

    result = await translate_text(text, target_lang=translate_to, source_lang="auto")
    db.log_history(message.from_user.id, "text", text, result)

    flag, name = LANGUAGES.get(translate_to, ("🌐", translate_to))
    await message.answer(f"{flag} <b>{name}</b>:\n\n{result}")


def _looks_like(text: str, lang_code: str) -> bool:
    """Juda oddiy heuristika: kirill alifbosi ruscha/tojikcha, lotincha - o'zbek/inglizcha va h.k."""
    cyrillic = any("а" <= ch.lower() <= "я" or ch.lower() == "ё" for ch in text)
    if lang_code in ("ru", "tg", "kk", "ky"):
        return cyrillic
    return not cyrillic
