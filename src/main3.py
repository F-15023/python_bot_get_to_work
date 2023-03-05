from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import executor
from db import BotDB
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message,ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove)


BOT_TOKEN = '5140163343:AAGaFLxhYrbFMaZ0aV0SRxHNgpJ4J3ld6EE'
BotDB = BotDB('accountant.db')
storage: MemoryStorage = MemoryStorage()

bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(bot, storage=storage)


class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_name = State()  # Состояние ожидания ввода имени
    fill_driverorpass = State()  # Состояние ожидания выбора типа аккаунта
    fill_start_point = State()  # Состояние ожидания ввода точки отправки
    fill_end_point = State()  # Состояние ожидания ввода точки назначения
    fill_phone = State()  # Состояние ожидания загрузки фото
    fill_education = State()  # Состояние ожидания выбора образования
    fill_wish_news = State()  # Состояние ожидания выбора получать ли новости


async def process_start_command(message: Message):
    if BotDB.user_exists(message.from_user.id):
        await message.answer(text='Вы уже зарегистрированы. Мы свяжемся с Вами как только подберем Вам попутчиков\n\n'
                                  'Если Вы хотите обновить данные нажмите:/fillform')
    else:
        BotDB.add_user(message.from_user.id)
        await message.answer(text='Поехали Вместе - это бот для поиска попутчиков по пути на работу\n\n'
                              'Чтобы перейти к заполнению анкеты - '
                              'отправьте нажмите сюда: /fillform')


async def process_fillform_command(message: Message):
    await message.answer(text='Пожалуйста, введите Ваше имя')
    # Устанавливаем состояние ожидания ввода имени
    await FSMFillForm.fill_name.set()


async def warning_not_name(message: Message):
    await message.answer(text='То, что вы отправили не похоже на имя\n\n'
                              'Пожалуйста, введите ваше имя\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')


async def process_name_sent(message: Message, state: FSMContext):
    name = message.text
    BotDB.add_name(message.from_user.id,name)
    markup = InlineKeyboardMarkup()
    driver_button = InlineKeyboardButton(text='Водитель',                                         callback_data='driver')
    passanger_button = InlineKeyboardButton(text='Пассажир',                                            callback_data='passanger')
    driverandpass_button = InlineKeyboardButton(text='И водитель и пассажир',                                                callback_data='driverandpass')
    markup.add(driver_button, passanger_button).add(driverandpass_button)
    await message.answer(
        text='Спасибо!\n\nА теперь Укажите в качестве кого Вы хотите зарегистроваться, Водитель или Пассажир',
        reply_markup=markup)
    await FSMFillForm.fill_driverorpass.set()


async def warning_not_driverorpass(message: Message):
    await message.answer(text='Пожалуйста, пользуйтесь кнопками '
                              'при выборе пола\n\nЕсли вы хотите прервать '
                              'заполнение анкеты - отправьте команду /cancel')



async def process_driverorpass_press(callback: CallbackQuery, state: FSMContext):
    driverorpass = callback.data
    BotDB.add_record_driverorpass(callback.from_user.id, driverorpass)
        # Удаляем сообщение с кнопками
    await callback.message.delete()
    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.answer(text='Спасибо!\n\nА теперь укажите адрес, откуда Вы едите на работу')
    # Устанавливаем состояние ожидания ввода точки отправки
    await FSMFillForm.fill_start_point.set()


# Этот хэндлер будет срабатывать, если во время ввода точки отправки
# будет введено что-то некорректное
async def warning_not_startpoint(message: Message):
    await message.answer(
        text='Необходимо указать адресс откуда Вы едите на работу'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если введен корректная точка отправки
# и переводить в состояние выбора точки назначения
async def process_startpoint_sent(message: Message, state: FSMContext):
    # C помощью менеджера контекста сохраняем точку отправки
    # в хранилище по ключу "start_point"
    startpoint = message.text
    BotDB.add_startpoint(message.from_user.id, startpoint)
    await message.answer(text='Спасибо!\n\nА теперь укажите адрес Вашей работы')
    # Устанавливаем состояние ожидания ввода точки отправки
    await FSMFillForm.fill_end_point.set()


# Этот хэндлер будет срабатывать, если во время ввода точки назначения
# будет введено что-то некорректное
async def warning_not_endpoint(message: Message):
    await message.answer(
        text='Необходимо указать адресс откуда Вы едите на работу'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если введен корректная точка назначения
# и переводить в состояние поделиться номером телефона
async def process_endpoint_sent(message: Message, state: FSMContext):
    # C помощью менеджера контекста сохраняем точку отправки
    # в хранилище по ключу "end_point"
    endpoint = message.text
    BotDB.add_endpoint(message.from_user.id, endpoint)
    # Создаем объект инлайн-клавиатуры для расшаривания номера телефона
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # Создаем объекты инлайн-кнопок
    phone_number_button = KeyboardButton(text='Нажмите, чтобы поделиться номером телефона',
                                               request_contact=True)
    # Добавляем кнопки в клавиатуру (две в одном ряду и одну в другом)
    markup.row(phone_number_button)
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(text='Принято!\n\n И последнее, нужно поделиться Вашим номером телефона', reply_markup=markup)
    # Устанавливаем состояние ожидания ввода точки отправки
    await FSMFillForm.fill_phone.set()


## Этот хэндлер будет срабатывать, если во время ввода номера телефона
# будет введено что-то некорректное
async def warning_not_phone(message: Message):
    await message.answer(
        text='Необходимо указать номер телефона в формате: 89991649723\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')


# Тут должна быть функция по получению номера телефона
async def procces_phonenumber_sent(message: Message, state: FSMContext):

    phone = message.contact.phone_number
    BotDB.add_record_phone(message.from_user.id, phone)
    markup = ReplyKeyboardRemove()
    await state.finish()
    await message.answer(text='Спасибо! Вы завершили регистрацию!\n\n'
                                          'Вскоре мы подберем Вам попутчиков',reply_markup=markup)
    await message.answer(text='Спасибо!)')





# Этот хэндлер будет срабатывать на команду "/cancel"
# и отключать машину состояний
async def process_cancel_command(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из регистрации\n\n'
                              'Чтобы снова перейти к регистрации - '
                              'отправьте команду /fillform')
    await state.reset_state()


async def send_echo(message: Message):
    await message.reply(text='Извините, следуйте инструкциям по регистрации')


# Регистрируем хэндлеры
dp.register_message_handler(process_start_command,
                            commands='start')
dp.register_message_handler(process_fillform_command,
                            commands='fillform')
dp.register_message_handler(process_cancel_command,
                            commands='cancel',
                            state='*')

dp.register_message_handler(process_name_sent,
                            lambda x: x.text.isalpha(),
                            state=FSMFillForm.fill_name)
dp.register_message_handler(warning_not_name,
                            content_types='any',
                            state=FSMFillForm.fill_name)

dp.register_callback_query_handler(
    process_driverorpass_press,
    text=['driver', 'passanger', 'driverandpass'],
    state=FSMFillForm.fill_driverorpass)
dp.register_message_handler(warning_not_driverorpass,
                            content_types='any',
                            state=FSMFillForm.fill_driverorpass)

dp.register_message_handler(process_startpoint_sent,
                            content_types='any',
                            state=FSMFillForm.fill_start_point)
dp.register_message_handler(process_endpoint_sent,
                            content_types='any',
                            state=FSMFillForm.fill_end_point)

dp.register_message_handler(procces_phonenumber_sent,
                            content_types='any',
                            state=FSMFillForm.fill_phone)

dp.register_message_handler(send_echo, content_types='any')
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

