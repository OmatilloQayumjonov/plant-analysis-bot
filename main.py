import sys
import os

# 1. Loyihaning asosiy papkasini qat'iy ravishda sys.path ga qo'shish
# Bu Linux / Render / Docker muhitlarida "ModuleNotFoundError: No module named 'bot'" xatosini 100% bartaraf etadi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 2. Render bepul tarifida (512MB RAM) xotira yetishmasligi (OpenBLAS memory allocation) bo'lmasligi uchun
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import asyncio
import logging
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


async def start_web_server():
    """Render / Bulutli hostinglar uchun ping tinglovchi server (24/7 rejim uchun)"""
    port_str = os.getenv("PORT")
    if port_str:
        try:
            port = int(port_str)
            app = web.Application()

            async def handle_ping(request):
                return web.Response(text="🤖 Plant Chemical Analysis Bot is running 24/7!")

            app.router.add_get("/", handle_ping)
            app.router.add_get("/health", handle_ping)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", port)
            await site.start()
            logger.info(f"🌐 Cloud Web Server {port}-portda ishga tushdi va port ochiq.")
        except Exception as e:
            logger.warning(f"Web serverni ishga tushirishda xatolik: {e}")


async def main():
    # Render portini darhol ochish (Render portni skanerlab topishi uchun)
    await start_web_server()

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "=" * 60 + "\n"
            "[XATOLIK] BOT_TOKEN kiritilmagan!\n"
            "Iltimos, Render Environment Variables bo'limiga BOT_TOKEN qo'shing yoki\n"
            ".env faylini oching va bot tokenini kiriting:\n"
            "BOT_TOKEN=8939401003:AAGO2fMFsR489ZisMQO4DGZBETAt6W478ag\n"
            + "=" * 60
        )
        # Port ochiq turishi uchun cheksiz kutish (Render qayta-qayta crash bo'lib qolmasligi uchun)
        while True:
            await asyncio.sleep(3600)
        return

    logger.info("🤖 Plant Chemical Analysis (DPPH / IC50) bot ishga tushmoqda...")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Eski kutilayotgan yangilanishlarni tashlab yuborish
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        bot_info = await bot.get_me()
        logger.info(f"✅ Bot muvaffaqiyatli ulandi: @{bot_info.username} ({bot_info.first_name})")
    except Exception as e:
        logger.error(f"Telegram API ga ulanishda xatolik (Token noto'g'ri bo'lishi mumkin): {e}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
