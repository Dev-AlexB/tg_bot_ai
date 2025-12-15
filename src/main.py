import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import settings
from handlers.normal import router as normal_router
from handlers.other import router as other_router
from keyboards.menu import set_main_menu
from middlewares.log import LoggingMiddleware
from services.init_db import init_db


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=settings.log.level,
        format=settings.log.format,
    )

    logger.info("Initialising database...")
    await init_db()

    logger.info("Starting bot...")
    bot = Bot(token=settings.bot.token)
    dp = Dispatcher()

    logger.info("Setting main menu...")
    await set_main_menu(bot)

    logger.info("Including routers...")
    dp.include_routers(
        normal_router,
        other_router,
    )

    logger.info("Including middlewares...")
    dp.message.middleware(LoggingMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
