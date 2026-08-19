import os
import io
import asyncio
from dotenv import load_dotenv
from PIL import Image
import pytesseract
from pypdf import PdfReader
from docx import Document
from deep_translator import GoogleTranslator

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher(storage=MemoryStorage())

# Qo'llab-quvvatlanadigan asosiy tillar
LANGUAGES = {
    "🇺🇿 O'zbek": "uz",
    "🇷🇺 Rus": "ru",
    "🇬🇧 Ingliz": "en",
    "🇹🇷 Turk": "tr",
    "🇩🇪 Nemis": "de",
    "🇸🇦 Arab": "ar",
    "🇨🇳 Xitoy": "zh-CN",
    "🇰🇷 Koreys": "ko",
    "🇫🇷 Fransuz": "fr",
    "🇪🇸 Ispan": "es"
}

class BotStates(StatesGroup):
    choosing_lang_from = State()
    choosing_lang_to = State()
    text_translation = State()
    image_translation = State()
    doc_translation = State()

def get_main_menu():
    kb = [
        [KeyboardButton(text="✍️ Matn tarjima"), KeyboardButton(text="🖼 Rasm tarjima")],
        [KeyboardButton(text="📄 Hujjat tarjima"), KeyboardButton(text="⚙️ Tillarni almashtirish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_lang_keyboard(prefix: str):
    buttons = []
    row = []
    for name, code in LANGUAGES.items():
        row.append(InlineKeyboardButton(text=name, callback_data=f"{prefix}:{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def smart_translate(text: str, lang_from: str, lang_to: str) -> str:
    try:
        translator = GoogleTranslator(source=lang_from, target=lang_to)
        return translator.translate(text)
    except Exception as e:
        return f"Tarjima jarayonida xatolik: {str(e)}"

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "👋 **Xush kelibsiz!**\n\n"
        "Men universal tarjimon botman.\n"
        "Quyidagi bo'limlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.message(F.text.in_(["✍️ Matn tarjima", "⚙️ Tillarni almashtirish"]))
async def start_text_tarjima(message: Message, state: FSMContext):
    await state.set_state(BotStates.choosing_lang_from)
    await message.answer(
        "🌐 **Qaysi tildan tarjima qilasiz?** (Manba tilini tanlang):",
        reply_markup=get_lang_keyboard("src"),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("src:"))
async def select_source_lang(call: CallbackQuery, state: FSMContext):
    src_code = call.data.split(":")[1]
    await state.update_data(src_lang=src_code)
    await state.set_state(BotStates.choosing_lang_to)
    await call.message.edit_text(
        "🎯 **Qaysi tilga tarjima qilinsin?** (Natija tilini tanlang):",
        reply_markup=get_lang_keyboard("tgt"),
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(F.data.startswith("tgt:"))
async def select_target_lang(call: CallbackQuery, state: FSMContext):
    tgt_code = call.data.split(":")[1]
    data = await state.get_data()
    src_code = data.get("src_lang", "uz")
    
    await state.update_data(tgt_lang=tgt_code)
    await state.set_state(BotStates.text_translation)
    
    src_title = [k for k, v in LANGUAGES.items() if v == src_code]
    tgt_title = [k for k, v in LANGUAGES.items() if v == tgt_code]
    
    src_name = src_title[0] if src_title else src_code
    tgt_name = tgt_title[0] if tgt_title else tgt_code
    
    await call.message.edit_text(
        f"✅ **Sozlandi:** {src_name} ➡️ {tgt_name}\n\n"
        f"Endi matn yuboring. Bot avtomatik 2 tomonlama tarjima qilib beradi!",
        parse_mode="Markdown"
    )
    await call.answer()

@dp.message(BotStates.text_translation, F.text)
async def process_text_translation(message: Message, state: FSMContext):
    if message.text in ["✍️ Matn tarjima", "🖼 Rasm tarjima", "📄 Hujjat tarjima", "⚙️ Tillarni almashtirish"]:
        return
    
    data = await state.get_data()
    src_lang = data.get("src_lang", "uz")
    tgt_lang = data.get("tgt_lang", "ru")
    
    try:
        res = smart_translate(message.text, src_lang, tgt_lang)
        if res.strip().lower() == message.text.strip().lower():
            res = smart_translate(message.text, tgt_lang, src_lang)
        await message.reply(res)
    except Exception as e:
        await message.reply(f"Xatolik: {e}")

@dp.message(F.text == "🖼 Rasm tarjima")
async def ask_for_image(message: Message, state: FSMContext):
    await state.set_state(BotStates.image_translation)
    await message.answer("📷 Tarjima qilmoqchi bo'lgan rasmingizni yuboring:")

@dp.message(BotStates.image_translation, F.photo)
async def process_image_ocr(message: Message, state: FSMContext):
    data = await state.get_data()
    tgt_lang = data.get("tgt_lang", "uz")
    
    wait_msg = await message.answer("⏳ Rasm o'qilmoqda...")
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file.file_path)
        
        image = Image.open(io.BytesIO(file_bytes.read()))
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text.strip():
            await wait_msg.edit_text("❌ Rasmda matn topilmadi.")
            return
        
        translated = smart_translate(extracted_text, "auto", tgt_lang)
        await wait_msg.delete()
        await message.reply(
            f"📝 **Rasmdagi matn:**\n`{extracted_text[:500]}`\n\n🌐 **Tarjima:**\n{translated}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await wait_msg.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")

@dp.message(F.text == "📄 Hujjat tarjima")
async def ask_for_doc(message: Message, state: FSMContext):
    await state.set_state(BotStates.doc_translation)
    await message.answer("📄 Hujjatni yuboring (.txt, .docx yoki .pdf formatida):")

@dp.message(BotStates.doc_translation, F.document)
async def process_document(message: Message, state: FSMContext):
    data = await state.get_data()
    tgt_lang = data.get("tgt_lang", "uz")
    
    doc = message.document
    file = await bot.get_file(doc.file_id)
    file_bytes = await bot.download_file(file.file_path)
    content = ""
    
    wait_msg = await message.answer("⏳ Hujjat o'qilib, tarjima qilinmoqda...")
    try:
        if doc.file_name.endswith(".txt"):
            content = file_bytes.read().decode("utf-8", errors="ignore")
        elif doc.file_name.endswith(".docx"):
            docx_file = Document(io.BytesIO(file_bytes.read()))
            content = "\n".join([p.text for p in docx_file.paragraphs])
        elif doc.file_name.endswith(".pdf"):
            pdf_reader = PdfReader(io.BytesIO(file_bytes.read()))
            content = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        else:
            await wait_msg.edit_text("❌ Faqat TXT, DOCX yoki PDF formatlari qo'llab-quvvatlanadi.")
            return

        if not content.strip():
            await wait_msg.edit_text("❌ Hujjat ichida matn topilmadi.")
            return

        translated_text = smart_translate(content[:4000], "auto", tgt_lang)
        await wait_msg.delete()
        await message.reply(f"📄 **Hujjat tarjimasi:**\n\n{translated_text}")
    except Exception as e:
        await wait_msg.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")

async def main():
    if not bot:
        print("Iltimos, .env fayliga BOT_TOKEN kiriting!")
        return
    print("🚀 Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
