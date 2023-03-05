from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import executor
from aiogram.dispatcher.filters import Text

from db_postgres import DBPostgres
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove)

from main_test import dp


class StateRegistration(StatesGroup):
    choosing_role = State()
    choosing_name = State()
    choosing_phone = State()
    choosing_from_location = State()
    choosing_to_location = State()


# class StateGettingName(StatesGroup):
#     state = State()
#
#
# class StateGettingPhone(StatesGroup):
#     state = State()
#
#
# class StateGettingFromLocation(StatesGroup):
#     state = State()
#
#
# class StateGettingToLocation(StatesGroup):
#     state = State()


@dp.message_handler(Text(equals="Водитель"), state=StateRegistration.choosing_role.state)
async def message_handler(message: types.Message, state: FSMContext):
    # db.add_driver(tg_id)
    await state.finish()

    await message.reply("Укажите Ваше имя - как к Вам можно обращаться?", reply_markup=types.ReplyKeyboardRemove())
    await StateRegistration.choosing_name.set()


@dp.message_handler(Text(equals="Пассажир"), state=StateRegistration.choosing_role.state)
async def message_handler(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    # db.add_passenger(tg_id)
    await state.finish()

    await message.reply("Укажите Ваше имя - как к Вам можно обращаться?", reply_markup=types.ReplyKeyboardRemove())
    await StateRegistration.choosing_name.set()


@dp.message_handler(state=StateRegistration.choosing_name.state)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        name = message.text
        # db.add_name(tg_id, name)
        await state.finish()

        text = "Отлично, теперь укажите откуда вы едете на работу"
        await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
        await StateRegistration.choosing_from_location.set()
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Text(equals="Да"), state=StateRegistration.choosing_to_location.state)
async def message_handler(message: types.Message, state: FSMContext):
    print("Right address")
    tg_id = message.from_user.id
    point = "point"
    # db.writeFromPointForPassenger(tg_id, point)
    await state.finish()

    text = "Отлично, теперь укажите откуда вы едете на работу"
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await StateRegistration.choosing_from_location.set()


@dp.message_handler(Text(equals="Нет"), state=StateRegistration.choosing_to_location.state)
async def message_handler(message: types.Message):
    print("Wrong address")
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=StateRegistration.choosing_to_location.state)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        # Записываем и показываем
        text = "{address}"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Нет", "Да"]
        keyboard.add(*buttons)
        await message.reply(text + " - правильный адрес?", reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Text(equals="Да"), state=StateRegistration.choosing_from_location.state)
async def message_handler(message: types.Message, state: FSMContext):
    print("Right address2")
    tg_id = message.from_user.id
    point = "point"
    # db.writeFromPointForPassenger(tg_id, point)
    await state.finish()

    text = "Спасибо за регистрацию!"
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Text(equals="Нет"), state=StateRegistration.choosing_from_location.state)
async def message_handler(message: types.Message):
    print("Wrong address2")
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=StateRegistration.choosing_from_location.state)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        # Записываем и показываем
        text = "{address}"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Нет", "Да"]
        keyboard.add(*buttons)
        await message.reply(text + " - правильный адрес?", reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())
