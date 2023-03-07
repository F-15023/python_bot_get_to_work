from aiogram import types, Router, F
from aiogram.filters import Command, Text
from aiogram.fsm.state import StatesGroup, State
from src.pojo.geocoding import Geocoder
from src.pojo.user import User
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

router = Router()
geocoder = Geocoder()
user_by_id = {}


class StateRegistration(StatesGroup):
    choosing_role = State()
    choosing_name = State()
    choosing_phone = State()
    choosing_from_location = State()
    choosing_to_location = State()


@router.message(Command(commands=['start']))
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
    buttons = [[
        types.KeyboardButton(text="Нет, в другой раз..."),
        types.KeyboardButton(text="Заполнить")
    ]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
                                         resize_keyboard=True,
                                         one_time_keyboard=True,
                                         input_field_placeholder="Нажмите на одну из кнопок ниже")
    await message.answer(text, reply_markup=keyboard)


@router.message(Text(text=['Нет, в другой раз...']))
async def answer(message: types.Message):
    await message.reply("Ok)", reply_markup=types.ReplyKeyboardRemove())


@router.message(Text(text=["Заполнить"]))
async def answer(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    user = User()
    user_by_id[tg_id] = user

    buttons = [[
        types.KeyboardButton(text="Водитель"),
        types.KeyboardButton(text="Пассажир")
    ]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Нажмите на одну из кнопок ниже")

    text = 'Отлично! Скажите, вы регистрируетесь как Водитель или Пассажир?'
    await message.reply(text, reply_markup=keyboard)
    await state.set_state(StateRegistration.choosing_role)


# choosing_role----------------------------------------------------------------------------------------------

@router.message(StateRegistration.choosing_role)
@router.message(F.text.in_("Водитель"))
async def message_handler(message: types.Message, state: FSMContext):
    user: User = user_by_id[message.from_user.id]
    user.role = "driver"
    await message.reply("Укажите Ваше имя - как к Вам можно обращаться?", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(StateRegistration.choosing_name)


@router.message(StateRegistration.choosing_role)
@router.message(F.text.in_("Пассажир"))
async def message_handler(message: types.Message, state: FSMContext):
    user: User = user_by_id[message.from_user.id]
    user.role = "passenger"
    await message.reply("Укажите Ваше имя - как к Вам можно обращаться?", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(StateRegistration.choosing_name)


# choosing_name----------------------------------------------------------------------------------------------

@router.message(StateRegistration.choosing_name)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        user: User = user_by_id[message.from_user.id]
        user.name = message.text
        buttons = [[
            types.KeyboardButton(text='Нажмите, чтобы поделиться номером телефона',
                                 request_contact=True)
        ]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Нажмите на одну из кнопок ниже")
        text = "Напишите или поделитесь привязанным к аккаунту телеграмма номером телефона"
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(StateRegistration.choosing_phone)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_phone----------------------------------------------------------------------------------------------

@router.message(StateRegistration.choosing_phone, F.text.in_("Да"))
async def message_handler(message: types.Message, state: FSMContext):
    await message.reply("Отлично, теперь укажите откуда вы едете на работу", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(StateRegistration.choosing_from_location)


@router.message(StateRegistration.choosing_phone, F.text.in_("Нет"))
async def message_handler(message: types.Message):
    print("Wrong phone")
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@router.message(StateRegistration.choosing_phone)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        if message.text is not None:
            phone = message.text
        else:
            phone = message.contact.phone_number
        user: User = user_by_id[message.from_user.id]
        user.phone = phone
        buttons = [[
            types.KeyboardButton(text="Нет"),
            types.KeyboardButton(text="Да")
        ]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Нажмите на одну из кнопок ниже")
        text = phone + " - Ваш номер телефона?"
        await message.reply(text, reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_from_location----------------------------------------------------------------------------------------------

@router.message(StateRegistration.choosing_from_location, F.text.in_("Да"))
async def message_handler(message: types.Message, state: FSMContext):
    await message.reply("Отлично, теперь укажите куда вы едете на работу", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(StateRegistration.choosing_to_location)


@router.message(StateRegistration.choosing_from_location, F.text.in_("Нет"))
async def message_handler(message: types.Message):
    print(message.text)
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@router.message(StateRegistration.choosing_from_location)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        lat, lon = geocoder.get_coordinates_by_text(message.text)
        wkt = f"POINT({lon},{lat})"

        user: User = user_by_id[message.from_user.id]
        user.from_location = wkt

        buttons = [[
            types.KeyboardButton(text="Нет"),
            types.KeyboardButton(text="Да")
        ]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Нажмите на одну из кнопок ниже")
        osm_ref = f"https://www.openstreetmap.org/#map=17/{lon}/{lat}"
        await message.reply(osm_ref + " - правильный адрес?", reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())


# choosing_to_location----------------------------------------------------------------------------------------------

@router.message(StateRegistration.choosing_to_location, F.text.in_("Да"))
async def message_handler(message: types.Message, state: FSMContext):
    user_by_id.pop(message.from_user.id, None)
    # db.write_do_db(user_by_id.[message.from_user.id]
    await message.reply("Спасибо за регистрацию!", reply_markup=types.ReplyKeyboardRemove())


@router.message(StateRegistration.choosing_to_location, F.text.in_("Нет"))
async def message_handler(message: types.Message):
    await message.reply("Попробуйте указать еще раз", reply_markup=types.ReplyKeyboardRemove())


@router.message(StateRegistration.choosing_to_location)
async def message_handler(message: types.Message, state: FSMContext):
    try:
        lat, lon = geocoder.get_coordinates_by_text(message.text)
        wkt = f"POINT({lon},{lat})"

        user: User = user_by_id[message.from_user.id]
        user.to_location = wkt

        buttons = [[
            types.KeyboardButton(text="Нет"),
            types.KeyboardButton(text="Да")
        ]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Нажмите на одну из кнопок ниже")
        osm_ref = f"https://www.openstreetmap.org/#map=17/{lon}/{lat}"

        await message.reply(osm_ref + " - правильный адрес?", reply_markup=keyboard)
    except Exception:
        await message.reply("Что-то пошло не так...", reply_markup=types.ReplyKeyboardRemove())

# end_of_registration ----------------------------------------------------------------------------------------------
