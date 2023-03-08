from aiogram import types, Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.state import StatesGroup, State
from src.pojo.geocoding import Geocoder
from src.pojo.user import User
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

router = Router()


class StateRegistration(StatesGroup):
    choosing_role = State()
    choosing_name = State()

@router.message(Command(commands=['start']))
async def answer(message: types.Message):
    text = 'Поехали Вместе - это бот для поиска попутчиков по пути на работу.' \
           ' {Далее идет краткое описание работы бота}.' \
           ' Для использования бота нужно заполнить анкету. Заполнить сейчас?'
    buttons = [
        [
            types.KeyboardButton(text="Нет, в другой раз..."),
            types.KeyboardButton(text="Заполнить")
        ],
        [types.KeyboardButton(text="Я зарегистрирован, но хочу удалить мои данные")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
                                         resize_keyboard=True,
                                         one_time_keyboard=True,
                                         input_field_placeholder="Нажмите на одну из кнопок ниже")
    await message.answer(text, reply_markup=keyboard)


@router.message(Text(text=['Нет, в другой раз...']))
async def answer(message: types.Message):
    await message.reply("Ok)", reply_markup=types.ReplyKeyboardRemove())
