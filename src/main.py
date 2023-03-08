import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.state import StatesGroup, State

from handlers import registration
from src.handlers import start, driver, passenger


async def main():
    BOT_TOKEN = '5140163343:AAGaFLxhYrbFMaZ0aV0SRxHNgpJ4J3ld6EE'
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(driver.router)
    dp.include_router(passenger.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
