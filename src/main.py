from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.geocoding import Geocoder

BOT_TOKEN = '5140163343:AAGaFLxhYrbFMaZ0aV0SRxHNgpJ4J3ld6EE'
storage: MemoryStorage = MemoryStorage()
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(bot, storage=storage)
geocoder = Geocoder()

id_to_text = {}


@dp.message_handler(commands=['start'])
async def answer(message: types.Message):
    text = 'Поехали Вместе - это бот для поиска попутчиков по пути на работу.' \
           ' {Далее идет краткое описание работы бота}.' \
           ' Для использования бота нужно заполнить анкету. Заполнить сейчас?'
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["Нет, в другой раз...", "Заполнить"]
    keyboard.add(*buttons)
    await message.answer(text, reply_markup=keyboard)


@dp.message_handler(Text(equals="Заполнить"))
async def answer(message: types.Message):
    text = 'Отлично! Скажите, вы регистрируетесь как Водитель или Пассажир?'
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["Водитель", "Пассажир"]
    keyboard.add(*buttons)
    await message.reply(text, reply_markup=keyboard)
    await StateRegistration.choosing_role.set()


@dp.message_handler(Text(equals='Нет, в другой раз...'))
async def answer(message: types.Message):
    await message.reply("Ok)", reply_markup=types.ReplyKeyboardRemove())


class StateRegistration(StatesGroup):
    choosing_role = State()
    choosing_name = State()
    choosing_phone = State()
    choosing_from_location = State()
    choosing_to_location = State()


# choosing_role----------------------------------------------------------------------------------------------

@dp.message_handler(Text(equals="Водитель"), state=StateRegistration.choosing_role)
async def message_handler(message: types.Message, state: FSMContext):
    # db.add_driver(tg_id)
    await state.finish()

    await message.reply("Укажите Ваше имя - как к Вам можно обращаться?", reply_markup=types.ReplyKeyboardRemove())
    await StateRegistration.choosing_name.set()


@dp.message_handler(Text(equals="Пассажир"), state=StateRegistration.choosing_role)
async def message_handler(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    # db.add_passenger(tg_id)
    await state.finish()

    await message.reply("Укажите Ваше имя - как к Вам можно обращаться?", reply_markup=types.ReplyKeyboardRemove())
    await StateRegistration.choosing_name.set()


# choosing_name----------------------------------------------------------------------------------------------

@dp.message_handler(state=StateRegistration.choosing_name)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        name = message.text
        # db.add_name(tg_id, name)
        await state.finish()

        text = "Напишите или поделитесь привязанным к аккаунту телеграмма номером телефона"
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        phone_number_button = KeyboardButton(text='Нажмите, чтобы поделиться номером телефона',
                                             request_contact=True)
        keyboard.add(phone_number_button)
        await message.answer(text, reply_markup=keyboard)
        await StateRegistration.choosing_phone.set()
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_phone----------------------------------------------------------------------------------------------

@dp.message_handler(Text(equals="Да"), state=StateRegistration.choosing_phone)
async def message_handler(message: types.Message, state: FSMContext):
    print("Right address2")
    tg_id = message.from_user.id
    phone = id_to_text[tg_id]
    # db.save_phone(tg_id, phone)
    await state.finish()

    text = "Отлично, теперь укажите откуда вы едете на работу"
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await StateRegistration.choosing_from_location.set()


@dp.message_handler(Text(equals="Нет"), state=StateRegistration.choosing_phone)
async def message_handler(message: types.Message):
    print("Wrong phone")
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=StateRegistration.choosing_phone, content_types='any')
async def message_handler(message: types.Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        phone = message.text
        id_to_text[tg_id] = phone
        if message.text is not None:
            phone = message.text
        else:
            phone = message.contact.phone_number
        text = phone + " - Ваш номер телефона?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Нет", "Да"]
        keyboard.add(*buttons)
        await message.reply(text, reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_from_location----------------------------------------------------------------------------------------------

@dp.message_handler(Text(equals="Да"), state=StateRegistration.choosing_from_location)
async def message_handler(message: types.Message, state: FSMContext):
    print(message.text)
    tg_id = message.from_user.id
    wkt = id_to_text[tg_id]
    # db.add_from_location(tg_id, wkt)
    await state.finish()

    text = "Отлично, теперь укажите куда вы едете на работу"
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await StateRegistration.choosing_to_location.set()


@dp.message_handler(Text(equals="Нет"), state=StateRegistration.choosing_from_location)
async def message_handler(message: types.Message):
    print(message.text)
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=StateRegistration.choosing_from_location)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        lat, lon = geocoder.get_coordinates_by_text(message.text)
        wkt = f"POINT({lon},{lat})"
        id_to_text[tg_id] = wkt
        osm_ref = f"https://www.openstreetmap.org/#map=17/{lon}/{lat}"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Нет", "Да"]
        keyboard.add(*buttons)
        await message.reply(osm_ref + " - правильный адрес?", reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_to_location----------------------------------------------------------------------------------------------

@dp.message_handler(Text(equals="Да"), state=StateRegistration.choosing_to_location)
async def message_handler(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    wkt = id_to_text[tg_id]
    # db.add_to_location(tg_id, wkt)
    await state.finish()

    text = "Спасибо за регистрацию!"
    id_to_text.pop(tg_id, None)
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Text(equals="Нет"), state=StateRegistration.choosing_to_location.state)
async def message_handler(message: types.Message):
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=StateRegistration.choosing_to_location.state)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        lat, lon = geocoder.get_coordinates_by_text(message.text)
        wkt = f"POINT({lon},{lat})"
        id_to_text[tg_id] = wkt
        osm_ref = f"https://www.openstreetmap.org/#map=17/{lon}/{lat}"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Нет", "Да"]
        keyboard.add(*buttons)
        await message.reply(osm_ref + " - правильный адрес?", reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())

# end_of_registration ----------------------------------------------------------------------------------------------
