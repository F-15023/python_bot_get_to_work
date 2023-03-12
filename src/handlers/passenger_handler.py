from aiogram import types, Router, F, Bot
from aiogram.filters import Command, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.dao.db_postgres import DBPostgres
from src.utils.client import Client

router = Router()
db = DBPostgres()
BOT_TOKEN = '5140163343:AAGaFLxhYrbFMaZ0aV0SRxHNgpJ4J3ld6EE'
my_bot: Bot = Bot(token=BOT_TOKEN)


@router.message(Text(text=['Показать ближайших водителей']))
async def answer(message: types.Message):
    uid = message.from_user.id
    drivers = db.get_drivers_near_passenger(uid)

    for element in drivers:
        driver: Client = element

        chat_info = await my_bot.get_chat(int(driver.tg_id))
        print(chat_info)
        text = f"[id={driver.tg_id}]\n" \
               f"Телефон={driver.phone}\n" \
               f"Имя={driver.name}\n" \
               f"Расстояние от моей начальной точки до маршрута водителя={int(driver.distance_from)} м\n" \
               f"Расстояние от моей конечной точки  до маршрута водителя={int(driver.distance_to)} м\n"

        builder = InlineKeyboardBuilder()
        builder.button(text=f"@{chat_info.username}", callback_data="send_passenger_hello")
        await my_bot.send_message(message.from_user.id, text=text, reply_markup=builder.as_markup())


@router.callback_query(Text("send_passenger_hello"))
async def send_random_value(callback: types.CallbackQuery):
    print("test send")
    await my_bot.send_message(429824727, "test message: 429824727")
