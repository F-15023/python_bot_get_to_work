from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.state import StatesGroup, State

from src.dao.db_postgres import DBPostgres
from src.pojo.geocoding import Geocoder
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from src.pojo.utils import *

router = Router()
geocoder = Geocoder()
user_by_id = {}
db = DBPostgres()


class States(StatesGroup):
    registration = State()
    driver = State()
    passenger = State()
    choosing_role = State()
    choosing_name = State()
    choosing_phone = State()
    choosing_from_location = State()
    choosing_to_location = State()


@router.message(Command(commands=['start']))
async def answer(message: types.Message, state: FSMContext):
    db.show_postgres_version()
    uid = message.from_user.id

    if db.is_user_exists(uid):
        if db.get_user_role(uid) in 'driver':
            buttons = [
                [
                    types.KeyboardButton(text="Показать ближайших пассажиров"),
                ],
                [types.KeyboardButton(text="Я зарегистрирован, но хочу удалить мои данные")]
            ]
            text = 'Готов к работе'
            await state.set_state(States.driver)
        else:
            buttons = [
                [
                    types.KeyboardButton(text="Показать ближайших водителей"),
                ],
                [types.KeyboardButton(text="Я зарегистрирован, но хочу удалить мои данные")]
            ]
            text = 'Готов к работе'
            await state.set_state(States.passenger)

    else:
        buttons = [
            [
                types.KeyboardButton(text="Нет, в другой раз..."),
                types.KeyboardButton(text="Заполнить")
            ]
        ]
        text = 'Поехали Вместе - это бот для поиска попутчиков по пути на работу.' \
               ' {Далее идет краткое описание работы бота}.' \
               ' Для использования бота нужно заполнить анкету. Заполнить сейчас?'
        await state.set_state(States.registration)

    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
                                         resize_keyboard=True,
                                         one_time_keyboard=False,
                                         input_field_placeholder="Нажмите на одну из кнопок ниже")
    await message.answer(text, reply_markup=keyboard)


@router.message(Text(text=["Я зарегистрирован, но хочу удалить мои данные"]))
async def answer(message: types.Message):
    db.drop_user(message.from_user.id)
    await message.reply("Ваши данные удалены", reply_markup=types.ReplyKeyboardRemove())
