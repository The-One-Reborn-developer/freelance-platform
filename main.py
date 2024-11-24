import os
import asyncio

from aiogram import Bot, Dispatcher

from dotenv import load_dotenv, find_dotenv

from app.tasks.celery_app import create_tables_task

from app.routers.start import start_router
from app.routers.menu import menu_router
from app.routers.profile import profile_router
from app.routers.new_bid import new_bid_router
from app.routers.search_bids import search_bids_router
from app.routers.look_bids import look_bids_router
from app.routers.look_chats import look_chats_router
from app.routers.chat_answer import chat_answer_router


load_dotenv(find_dotenv())


async def on_startup() -> None:
    create_tables_task.delay()

    try:
        bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'))
        dp = Dispatcher()
        dp.include_routers(start_router,
                           menu_router,
                           profile_router,
                           new_bid_router,
                           search_bids_router,
                           look_bids_router,
                           look_chats_router,
                           chat_answer_router)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f'Error starting bot: {e}')


if __name__ == '__main__':
    asyncio.run(on_startup())