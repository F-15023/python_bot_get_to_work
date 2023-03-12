from aiogram import types, Router, F
from aiogram.filters import Command, Text
from src.dao.db_postgres import DBPostgres
from src.handlers.start import States

router = Router()
db = DBPostgres()


@router.message(Text(text=['Показать ближайших водителей']))
async def answer(message: types.Message):
    uid = message.from_user.id
    text = db.get_drivers_near_passenger(uid)
    await message.reply(text)
