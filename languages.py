from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import LANGUAGES


def languages_kb(prefix: str) -> InlineKeyboardMarkup:
    """
    prefix: 'src' (manba til) yoki 'tgt' (tarjima tili) uchun callback_data prefiksi
    """
    buttons = []
    row = []
    for code, (flag, name) in LANGUAGES.items():
        row.append(InlineKeyboardButton(text=f"{flag} {name}", callback_data=f"{prefix}:{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
