from aiogram import types, Router, F, Bot
from aiogram.filters import Command, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.dao.db_postgres import DBPostgres
from src.utils.client import Client

router = Router()
db = DBPostgres()
BOT_TOKEN = '5140163343:AAGaFLxhYrbFMaZ0aV0SRxHNgpJ4J3ld6EE'
my_bot: Bot = Bot(token=BOT_TOKEN)


@router.message(Text(text=['Показать ближайших пассажиров']))
async def answer(message: types.Message):
    uid = message.from_user.id
    drivers = db.get_passengers_near_driver(uid)

    for element in drivers:
        passenger: Client = element

        chat_info = await my_bot.get_chat(int(passenger.tg_id))
        print(chat_info)
        text = f"[id={passenger.tg_id}]\n" \
               f"Телефон={passenger.phone}\n" \
               f"Имя={passenger.name}\n" \
               f"Расстояние от моей начальной точки до маршрута водителя={int(passenger.distance_from)} м\n" \
               f"Расстояние от моей конечной точки  до маршрута водителя={int(passenger.distance_to)} м\n"

        builder = InlineKeyboardBuilder()
        builder.button(text=f"@{chat_info.username}", callback_data="send_driver_hello")
        await my_bot.send_message(message.from_user.id, text=text, reply_markup=builder.as_markup())


@router.callback_query(Text("send_driver_hello"))
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer("send hello")
