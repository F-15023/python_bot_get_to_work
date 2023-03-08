from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.pojo.geocoding import Geocoder
from src.pojo.user import User

BOT_TOKEN = '5140163343:AAGaFLxhYrbFMaZ0aV0SRxHNgpJ4J3ld6EE'
storage: MemoryStorage = MemoryStorage()
bot: Bot = Bot(BOT_TOKEN)
dispatcher: Dispatcher = Dispatcher(bot, storage=storage)
geocoder = Geocoder()
user_by_id = {}


@dispatcher.message_handler(commands=['start'])
async def answer(message: types.Message):
    text = 'Поехали Вместе - это бот для поиска попутчиков по пути на работу.' \
           ' {Далее идет краткое описание работы бота}.' \
           ' Для использования бота нужно заполнить анкету. Заполнить сейчас?'

    # if db.is_user_exist(message.from_user.id):
    #     print("start standart work")
    #     return
    #
    # if not db.is_users_registration_done(message.from_user.id):
    #     await message.answer("Похоже в прошлый раз вы не завершили регистрацию полностью. Придется пройти ее заново",
    #                          reply_markup=types.ReplyKeyboardRemove())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["Нет, в другой раз...", "Заполнить"]
    keyboard.add(*buttons)
    await message.answer(text, reply_markup=keyboard)


@dispatcher.message_handler(Text(equals="Заполнить"))
async def answer(message: types.Message):
    tg_id = message.from_user.id
    user = User()
    user_by_id[tg_id] = user

    text = 'Отлично! Скажите, вы регистрируетесь как Водитель или Пассажир?'
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["Водитель", "Пассажир"]
    keyboard.add(*buttons)
    await message.reply(text, reply_markup=keyboard)
    await States.choosing_role.set()


@dispatcher.message_handler(Text(equals='Нет, в другой раз...'))
async def answer(message: types.Message):
    await message.reply("Ok)", reply_markup=types.ReplyKeyboardRemove())


class States(StatesGroup):
    choosing_role = State()
    choosing_name = State()
    choosing_phone = State()
    choosing_from_location = State()
    choosing_to_location = State()


# choosing_role----------------------------------------------------------------------------------------------

@dispatcher.message_handler(Text(equals="Водитель"), state=States.choosing_role)
async def message_handler(message: types.Message, state: FSMContext):
    user: User = user_by_id[message.from_user.id]
    user.role = "driver"
    await state.finish()

    await message.reply("Укажите Ваше имя - как к Вам можно обращаться?", reply_markup=types.ReplyKeyboardRemove())
    await States.choosing_name.set()


@dispatcher.message_handler(Text(equals="Пассажир"), state=States.choosing_role)
async def message_handler(message: types.Message, state: FSMContext):
    user: User = user_by_id[message.from_user.id]
    user.role = "passenger"
    await state.finish()

    await message.reply("Укажите Ваше имя - как к Вам можно обращаться?", reply_markup=types.ReplyKeyboardRemove())
    await States.choosing_name.set()


# choosing_name----------------------------------------------------------------------------------------------

@dispatcher.message_handler(state=States.choosing_name)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        user: User = user_by_id[message.from_user.id]
        user.name = message.text
        await state.finish()

        text = "Напишите или поделитесь привязанным к аккаунту телеграмма номером телефона"
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        phone_number_button = KeyboardButton(text='Нажмите, чтобы поделиться номером телефона',
                                             request_contact=True)
        keyboard.add(phone_number_button)
        await message.answer(text, reply_markup=keyboard)
        await States.choosing_phone.set()
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_phone----------------------------------------------------------------------------------------------

@dispatcher.message_handler(Text(equals="Да"), state=States.choosing_phone)
async def message_handler(message: types.Message, state: FSMContext):
    await state.finish()

    text = "Отлично, теперь укажите откуда вы едете на работу"
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await States.choosing_from_location.set()


@dispatcher.message_handler(Text(equals="Нет"), state=States.choosing_phone)
async def message_handler(message: types.Message):
    print("Wrong phone")
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@dispatcher.message_handler(state=States.choosing_phone, content_types='any')
async def message_handler(message: types.Message, state: FSMContext):
    try:
        if message.text is not None:
            phone = message.text
        else:
            phone = message.contact.phone_number

        user: User = user_by_id[message.from_user.id]
        user.phone = phone

        text = phone + " - Ваш номер телефона?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Нет", "Да"]
        keyboard.add(*buttons)
        await message.reply(text, reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_from_location----------------------------------------------------------------------------------------------

@dispatcher.message_handler(Text(equals="Да"), state=States.choosing_from_location)
async def message_handler(message: types.Message, state: FSMContext):
    await state.finish()

    text = "Отлично, теперь укажите куда вы едете на работу"
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await States.choosing_to_location.set()


@dispatcher.message_handler(Text(equals="Нет"), state=States.choosing_from_location)
async def message_handler(message: types.Message):
    print(message.text)
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@dispatcher.message_handler(state=States.choosing_from_location)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        lat, lon = geocoder.get_coordinates_by_text(message.text)
        wkt = f"POINT({lon},{lat})"

        user: User = user_by_id[message.from_user.id]
        user.from_location = wkt

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Нет", "Да"]
        keyboard.add(*buttons)
        osm_ref = f"https://www.openstreetmap.org/#map=17/{lon}/{lat}"
        await message.reply(osm_ref + " - правильный адрес?", reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_to_location----------------------------------------------------------------------------------------------

@dispatcher.message_handler(Text(equals="Да"), state=States.choosing_to_location)
async def message_handler(message: types.Message, state: FSMContext):
    await state.finish()

    text = "Спасибо за регистрацию!"
    user_by_id.pop(message.from_user.id, None)
    # db.write_do_db(user_by_id.[message.from_user.id]
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())


@dispatcher.message_handler(Text(equals="Нет"), state=States.choosing_to_location.state)
async def message_handler(message: types.Message):
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@dispatcher.message_handler(state=States.choosing_to_location.state)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        lat, lon = geocoder.get_coordinates_by_text(message.text)
        wkt = f"POINT({lon},{lat})"

        user: User = user_by_id[message.from_user.id]
        user.to_location = wkt

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Нет", "Да"]
        keyboard.add(*buttons)
        osm_ref = f"https://www.openstreetmap.org/#map=17/{lon}/{lat}"

        await message.reply(osm_ref + " - правильный адрес?", reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())

# end_of_registration ----------------------------------------------------------------------------------------------
