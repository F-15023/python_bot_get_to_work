from aiogram import types


def get_buttons_for_passenger():
    buttons = [
        [
            types.KeyboardButton(text="Показать ближайших водителей"),
        ],
        [types.KeyboardButton(text="Я зарегистрирован, но хочу удалить мои данные")]
    ]
    return buttons


def get_buttons_for_driver():
    buttons = [
        [
            types.KeyboardButton(text="Показать ближайших пассажиров"),
        ],
        [types.KeyboardButton(text="Я зарегистрирован, но хочу удалить мои данные")]
    ]
    return buttons


def get_buttons_for_registration():
    buttons = [
        [
            types.KeyboardButton(text="Нет, в другой раз..."),
            types.KeyboardButton(text="Заполнить")
        ]
    ]
    return buttons


class Utils:
    pass
