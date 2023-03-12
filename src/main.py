import asyncio
from aiogram import Bot, Dispatcher

from src.dao.db_postgres import DBPostgres
from src.handlers import start_handler, driver_handler, passenger_handler, registration_handler


async def run():
    BOT_TOKEN = '5140163343:AAGaFLxhYrbFMaZ0aV0SRxHNgpJ4J3ld6EE'
    my_bot: Bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_handler.router)
    dp.include_router(registration_handler.router)
    dp.include_router(driver_handler.router)
    dp.include_router(passenger_handler.router)
    await my_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(my_bot)


if __name__ == "__main__":
    asyncio.run(run())
