from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from Database import db_telegram_bot as db

# Кнопки

button_main_menu = InlineKeyboardButton(text="Информация", callback_data="Info")
button_back_to_menu = InlineKeyboardButton(
    text="В главное меню", callback_data="Back_to_menu"
)
button_send_file = InlineKeyboardButton(text="Документ", callback_data='File')

# Маркап: вывод прикрепленного файла

kb_client_attach_file = InlineKeyboardMarkup()
kb_client_attach_file.add(button_send_file, button_back_to_menu)


# Маркап: возврат в меню

kb_client_info = InlineKeyboardMarkup()
kb_client_info.add(button_back_to_menu)


# Функция для создания маркапов с копманиями, отделами и вопросами
def genmarkup(data, USER_ID):  # передаём в функцию data
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    if db.valid_id(USER_ID) != 1:
        for i in data:  # цикл для создания кнопок
            markup.add(
                InlineKeyboardButton(data[i], callback_data=i)
            )  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
        return markup  # возвращаем клавиатуру
    else:
        markup.add(button_main_menu)
        for i in data:  # цикл для создания кнопок
            markup.add(
                InlineKeyboardButton(data[i], callback_data=i)
            )  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
        return markup  # возвращаем клавиатуру
