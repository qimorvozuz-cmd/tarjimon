import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ANTHROPIC_API_KEY
import database as db

from handlers import start, text, image, document, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
        raise RuntimeError(
            "BOT_TOKEN topilmadi. Railway'da Variables bo'limiga yoki config.py ga tokeningizni qo'shing."
        )
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "PUT_YOUR_ANTHROPIC_KEY_HERE":
        raise RuntimeError(
            "ANTHROPIC_API_KEY topilmadi. Railway'da Variables bo'limiga yoki config.py ga "
            "Claude API kalitingizni qo'shing."
        )

    db.init_db()
    logger.info("Ma'lumotlar bazasi tayyor.")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Handlerlar tartibi muhim: admin va maxsus rejimlar oldin, umumiy matn oxirida
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(image.router)
    dp.include_router(document.router)
    dp.include_router(text.router)

    logger.info("Bot ishga tushmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
