from aiogram import types, Router, F
from aiogram.filters import Command, Text
from src.dao.db_postgres import DBPostgres
from src.handlers.start import States

router = Router()
db = DBPostgres()


@router.message(States.driver, Text(text=['Показать ближайших пассажиров']))
async def answer(message: types.Message):
    uid = message.from_user.id
    text = db.get_passengers_near_driver_route(uid)
    await message.reply(text)
