from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
from config import LANGUAGES
from keyboards.menu import main_menu, MAIN_MENU_BTNS
from keyboards.languages import languages_kb

router = Router()


class LangSetup(StatesGroup):
    choosing_source = State()
    choosing_target = State()


WELCOME = (
    "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
    "Men <b>AI Tarjimon</b> botiman. Men orqali:\n"
    "📝 Matn\n"
    "🖼 Rasm (ichidagi yozuv)\n"
    "📄 Hujjat (PDF, DOCX, TXT)\n\n"
    "larni istalgan tilga tarjima qilishingiz mumkin.\n\n"
    "Boshlashdan oldin, qaysi tillar orasida tarjima qilishni tanlang 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    db.add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    await state.set_state(LangSetup.choosing_source)
    await message.answer(
        WELCOME.format(name=message.from_user.full_name),
        reply_markup=languages_kb("src"),
    )


@router.callback_query(F.data.startswith("src:"), LangSetup.choosing_source)
async def choose_source(callback: CallbackQuery, state: FSMContext):
    code = callback.data.split(":")[1]
    await state.update_data(source_lang=code)
    await state.set_state(LangSetup.choosing_target)
    flag, name = LANGUAGES[code]
    await callback.message.edit_text(
        f"✅ Manba til: {flag} {name}\n\nEndi qaysi tilga tarjima qilinsin?",
        reply_markup=languages_kb("tgt"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tgt:"), LangSetup.choosing_target)
async def choose_target(callback: CallbackQuery, state: FSMContext):
    code = callback.data.split(":")[1]
    data = await state.get_data()
    source_lang = data.get("source_lang", "uz")
    db.set_user_langs(callback.from_user.id, source_lang=source_lang, target_lang=code)
    await state.clear()

    src_flag, src_name = LANGUAGES[source_lang]
    tgt_flag, tgt_name = LANGUAGES[code]

    await callback.message.edit_text(
        f"🎉 Sozlandi!\n\n{src_flag} {src_name} → {tgt_flag} {tgt_name}\n\n"
        "Endi menyudan kerakli bo'limni tanlang yoki menga to'g'ridan-to'g'ri matn yuboring — "
        "men uni avtomatik tarjima qilaman."
    )
    await callback.message.answer("📋 Asosiy menyu:", reply_markup=main_menu())


@router.message(F.text == MAIN_MENU_BTNS["settings"])
async def open_settings(message: Message, state: FSMContext):
    await state.set_state(LangSetup.choosing_source)
    await message.answer(
        "Manba tilni tanlang (siz asosan qaysi tilda yozasiz):",
        reply_markup=languages_kb("src"),
    )


@router.message(F.text == MAIN_MENU_BTNS["help"])
async def open_help(message: Message):
    await message.answer(
        "🛟 <b>Yordam</b>\n\n"
        "📝 <b>Text tarjima</b> — menyudan tanlang yoki shunchaki matn yozing, avtomatik tarjima bo'ladi.\n"
        "🖼 <b>Rasm tarjima</b> — rasm yuboring, men ichidagi matnni o'qib tarjima qilaman.\n"
        "📄 <b>Hujjat tarjima</b> — PDF, DOCX yoki TXT yuboring, tarjima qilingan .docx qaytaraman.\n"
        "⚙️ <b>Til sozlamalari</b> — tarjima yo'nalishini istalgan payt o'zgartirishingiz mumkin.\n"
        "🕘 <b>Tarixim</b> — so'nggi tarjimalaringizni ko'rasiz.\n\n"
        "Savol bo'lsa, xabar yozing — admin sizga javob beradi."
    )
