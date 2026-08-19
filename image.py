from aiogram import Router, F
from aiogram.types import Message

import database as db
from config import LANGUAGES
from keyboards.menu import MAIN_MENU_BTNS
from services.ocr import extract_text_from_image, guess_tesseract_lang
from services.translate import translate_text

router = Router()


@router.message(F.text == MAIN_MENU_BTNS["image"])
async def image_mode_info(message: Message):
    await message.answer(
        "🖼 Ichida matn bo'lgan rasm yuboring (skrinshot, foto va h.k.) — "
        "men matnni o'qib, tarjima qilib beraman."
    )


@router.message(F.photo)
async def handle_photo(message: Message, bot):
    user = db.get_user(message.from_user.id) or {}
    src = user.get("source_lang", "uz")
    tgt = user.get("target_lang", "ru")

    status = await message.answer("🔎 Rasmdagi matn o'qilmoqda...")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)
    image_bytes = file_bytes.read()

    tess_lang = guess_tesseract_lang(src, tgt)
    extracted = await extract_text_from_image(image_bytes, lang_hint=tess_lang)

    if not extracted.strip():
        await status.edit_text(
            "⚠️ Rasmdan matn topilmadi. Rasm aniqroq yoki matn kattaroq bo'lishi kerak."
        )
        return

    await status.edit_text(f"📖 Topilgan matn:\n\n<code>{extracted[:1500]}</code>")

    translated = await translate_text(extracted, target_lang=tgt, source_lang="auto")
    db.log_history(message.from_user.id, "image", extracted, translated)

    flag, name = LANGUAGES.get(tgt, ("🌐", tgt))
    await message.answer(f"{flag} <b>{name}</b>:\n\n{translated}")
