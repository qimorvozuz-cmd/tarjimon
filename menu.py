from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

MAIN_MENU_BTNS = {
    "text": "📝 Text tarjima",
    "image": "🖼 Rasm tarjima",
    "document": "📄 Hujjat tarjima",
    "settings": "⚙️ Til sozlamalari",
    "history": "🕘 Tarixim",
    "help": "🛟 Yordam",
}


def main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=MAIN_MENU_BTNS["text"]), KeyboardButton(text=MAIN_MENU_BTNS["image"])],
        [KeyboardButton(text=MAIN_MENU_BTNS["document"]), KeyboardButton(text=MAIN_MENU_BTNS["settings"])],
        [KeyboardButton(text=MAIN_MENU_BTNS["history"]), KeyboardButton(text=MAIN_MENU_BTNS["help"])],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def cancel_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data="cancel")]]
    )


def admin_confirm_kb(target_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"adm_ok:{target_user_id}"),
                InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"adm_block:{target_user_id}"),
            ]
        ]
    )
