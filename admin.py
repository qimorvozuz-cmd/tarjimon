from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

import database as db
from config import ADMIN_IDS
from keyboards.menu import MAIN_MENU_BTNS

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not _is_admin(message.from_user.id):
        return
    stats = db.get_stats()
    by_kind = "\n".join(f"  • {k}: {v}" for k, v in stats["by_kind"].items()) or "  —"
    await message.answer(
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {stats['users']}\n"
        f"🔄 Jami tarjimalar: {stats['translations']}\n\n"
        f"Turlari bo'yicha:\n{by_kind}"
    )


@router.message(F.text == MAIN_MENU_BTNS["history"])
async def my_history(message: Message):
    rows = db.get_user_history(message.from_user.id, limit=10)
    if not rows:
        await message.answer("🕘 Sizda hali tarjima tarixi yo'q.")
        return
    lines = []
    for r in rows:
        src = (r["source_text"] or "")[:60]
        lines.append(f"• [{r['kind']}] {src}...")
    await message.answer("🕘 <b>So'nggi tarjimalaringiz:</b>\n\n" + "\n".join(lines))


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot):
    if not _is_admin(message.from_user.id):
        return
    text = message.text.replace("/broadcast", "", 1).strip()
    if not text:
        await message.answer("Foydalanish: /broadcast Xabar matni")
        return

    with db.get_conn() as conn:
        rows = conn.execute("SELECT user_id FROM users WHERE is_blocked = 0").fetchall()

    sent, failed = 0, 0
    for row in rows:
        try:
            await bot.send_message(row["user_id"], f"📢 {text}")
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"✅ Yuborildi: {sent} ta\n⚠️ Xato: {failed} ta")
