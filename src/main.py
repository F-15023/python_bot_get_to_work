import asyncio
from aiogram import Bot, Dispatcher
from handlers import registration


async def main():
    BOT_TOKEN = '5140163343:AAGaFLxhYrbFMaZ0aV0SRxHNgpJ4J3ld6EE'
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(registration.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
