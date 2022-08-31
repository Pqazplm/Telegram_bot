import json
import os
import random
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version
import asyncio

import folium
import langid
import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot_telegram_create import bot, dp
from Database import db_telegram_bot as db
from keyboards import genmarkup, kb_client_info, kb_client_attach_file

langid.set_languages(["en", "ru"])  # Для проверки языка
last_time = {}  # Для антиспама


# Класс для регистрации
class User(StatesGroup):
    Company = State()
    Center = State()
    Section = State()
    Name = State()
    Surname = State()
    Mail = State()
    Verification = State()


# Команда старта бота
@dp.message_handler(commands=["start"], state=None)
async def command_start(message: types.Message):
    USER_ID = message.from_user.id
    if db.valid_id(message.from_user.id) != 1:  # Если пользователь не зарегистрирован
        await User.Company.set()
        """with open("./json_files/Companies.json", "r", encoding="utf8") as f:
            data = json.load(f)"""
        await bot.send_message(
            message.from_user.id,
            "Выберите компанию:",
            reply_markup=genmarkup(db.show_me('companies'), USER_ID),
        )
    else:
        """with open("./json_files/Questions.json", "r", encoding="utf8") as f:
            data = json.load(f)"""
        data = db.show_me('questions')
        new_dict = {}
        user_section = db.return_section(USER_ID)
        for key in data:
            if user_section in key:
                new_dict.update({str(key): data[key]})

        await message.answer(
            "Вы уже зарегистрированы!", reply_markup=genmarkup(new_dict, USER_ID)
        )


# Регистрация id и компании в бд
@dp.callback_query_handler(state=User.Company)
async def menu_company(call: types.CallbackQuery, state: FSMContext):
    USER_ID = call.from_user.id
    async with state.proxy() as data:
        data["ID"] = USER_ID
        data["Company"] = call.data

    await User.next()
    """with open("./json_files/Sections.json", "r", encoding="utf8") as f:
        data = json.load(f)"""
    data = db.show_me('centers')
    new_dict = {}
    for key in data:
        if call.data in key:
            new_dict.update({str(key): data[key]})
    await call.message.edit_text(
        "Выберите центр:", reply_markup=genmarkup(new_dict, USER_ID)
    )
    await call.answer()


# Регистрация отдела в бд
@dp.callback_query_handler(state=User.Center)
async def menu_center(call: types.CallbackQuery, state: FSMContext):
    USER_ID = call.from_user.id
    async with state.proxy() as data:
        data["Center"] = call.data
    """with open("./json_files/Questions.json", "r", encoding="utf8") as f:
        data = json.load(f)"""
    data = db.show_me('sections')
    new_dict = {}
    for key in data:
        if call.data in key:
            new_dict.update({str(key): data[key]})
    await User.next()

    await call.message.edit_text("Выберите отдел", reply_markup=genmarkup(new_dict, USER_ID))
    await call.answer()


# Регистрация отдела в бд
@dp.callback_query_handler(state=User.Section)
async def menu_section(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["Section"] = call.data
    """with open("./json_files/Questions.json", "r", encoding="utf8") as f:
        data = json.load(f)"""
    data = db.show_me('questions')
    new_dict = {}
    for key in data:
        if call.data in key:
            new_dict.update({str(key): data[key]})
    await User.next()

    await call.message.edit_text("Введите имя")
    await call.answer()


# Регистрация имени в бд
@dp.message_handler(state=User.Name)
async def reg_surname(message: types.Message, state: FSMContext):
    lang, score = langid.classify(message.text)
    if lang != "ru":
        await message.answer("Поменяйте раскладку на русский язык!")
    else:
        async with state.proxy() as data:
            data["Name"] = message.text
        await User.next()
        await message.answer("Введите фамилию")


# Регистрация фамилии в бд
@dp.message_handler(state=User.Surname)
async def reg_number(message: types.Message, state: FSMContext):
    lang, score = langid.classify(message.text)
    if lang != "ru":
        await message.answer("Поменяйте раскладку на русский язык!")
    else:
        async with state.proxy() as data:
            data["Surname"] = message.text
        await User.next()
        await message.answer("Введите почту")


# Функция для отправки кода на почту
@dp.message_handler(state=User.Mail)
async def mail(message: types.Message, state: FSMContext):
    lang, score = langid.classify(message.text)
    if lang != "en":
        await message.answer("Поменяйте раскладку на английский язык!")
    else:
        global code
        code = random.sample("123456789", 4)
        code = str("".join(code))
        Mail = message.text
        async with state.proxy() as data:
            data["Mail"] = Mail

        sender = "arsenysharikov@yandex.ru"
        sender_password = "qbvmfawvvnijxtff"

        mail_lib = smtplib.SMTP_SSL("smtp.yandex.ru", 465)
        mail_lib.login(sender, sender_password)

        msg = (
            'From: %s\r\nTo: %s\r\nContent-Type: text/plain; charset="utf-8"\r\nSubject: %s\r\n\r\n'
            % ("PyProjectForHelp <" + sender + ">", Mail, "Тема сообщения")
        )
        msg += f"Ваш код регистрации: {code}"
        mail_lib.sendmail(sender, Mail, msg.encode("utf8"))
        mail_lib.quit()
        async with state.proxy() as data:
            data["Count"] = 0
        await db.add_data(state)
        await message.answer("Введите полученный код")
        await User.next()


# Функция для проверки правильности введенного кода
@dp.message_handler(state=User.Verification)
async def verification(message: types.Message, state: FSMContext):
    USER_ID = message.from_user.id
    if db.check(USER_ID):
        await db.del_data(USER_ID)
        await message.answer(f"Попытки исчерпаны... \nВведите команду /start через 2 минуты")
        time.sleep(120)
        await state.finish()
    else:
        if message.text == code:
            """with open("./json_files/Questions.json", "r", encoding="utf8") as f:
                data = json.load(f)"""
            data = db.show_me('questions')
            new_dict = {}
            user_section = db.return_section(USER_ID)
            for key in data:
                if user_section in key:
                    new_dict.update({str(key): data[key]})
            await message.answer(
                "Регистрация прошла успешно!",
                reply_markup=genmarkup(new_dict, USER_ID),
            )
            await state.finish()
        else:
            await message.answer("Код неверный!")
            db.add_count(1, USER_ID)


# Вывод маркапа с информация
@dp.callback_query_handler(text="Info")
async def info(call: types.CallbackQuery):
    await call.message.edit_text(
        "Абсолютно вся информация о том, как использовать бот...",
        reply_markup=kb_client_info,
    )
    await call.answer()


# Функция возврата в меню с вопросами
@dp.callback_query_handler(text="Back_to_menu")
async def back_to_menu(call: types.CallbackQuery):
    USER_ID = call.from_user.id
    """with open("./json_files/Questions.json", "r", encoding="utf8") as f:
        data = json.load(f)"""
    data = db.show_me('questions')
    new_dict = {}
    user_section = db.return_section(USER_ID)
    for key in data:
        if user_section in key:
            new_dict.update({str(key): data[key]})
    await call.message.edit_text("Меню", reply_markup=genmarkup(new_dict, USER_ID))
    await call.answer()


# Вывод маркапа с файлом
@dp.callback_query_handler(text="File")
async def attach_file(call: types.CallbackQuery):

    USER_ID = call.from_user.id
    src = os.path.abspath(db.show_answer(file_data + '_file'))

    if call.message.chat.id not in last_time:
        last_time[call.message.chat.id] = time.time()
    else:
        if (time.time() - last_time[call.message.chat.id]) * 1000 < 10000:
            return 0
        last_time[call.message.chat.id] = time.time()

    await call.message.answer_document(
        open(src, 'rb'),
    )
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    data = db.show_me('questions')
    new_dict = {}
    user_section = db.return_section(USER_ID)
    for key in data:
        if user_section in key:
            new_dict.update({str(key): data[key]})
    await call.message.answer("Меню", reply_markup=genmarkup(new_dict, USER_ID))
    await call.answer()


# Функция вывода ответа на вопрос
@dp.callback_query_handler()
async def show_answers(call: types.CallbackQuery):
    global file_data
    file_data = call.data
    answer = db.show_answer(call.data).replace("\\n", "\n")
    if '_f' in call.data:
        await call.message.edit_text(
            answer, reply_markup=kb_client_attach_file)
    else:
        await call.message.edit_text(
            answer, reply_markup=kb_client_info)
