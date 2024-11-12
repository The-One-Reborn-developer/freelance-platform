import os
import asyncio

from aiogram import Bot, Dispatcher

from dotenv import load_dotenv, find_dotenv

from app.database.queues.create_tables import create_tables

from app.routers.start import start_router
from app.routers.menu import menu_router
from app.routers.cities import cities_router
from app.routers.profile import profile_router


load_dotenv(find_dotenv())


async def on_startup() -> None:
    create_tables()

    try:
        bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'))
        dp = Dispatcher()
        dp.include_routers(start_router,
                           menu_router,
                           cities_router,
                           profile_router)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f'Error starting bot: {e}')


if __name__ == '__main__':
    asyncio.run(on_startup())