import sqlite3

from prettytable import MSWORD_FRIENDLY, from_db_cursor
from tabulate import tabulate
from itertools import chain

# создание базы данных
def db_start():
    global db, cur
    db = sqlite3.connect("telegram_bot.db")
    cur = db.cursor()
    # 1) создание таблицы информации о пользователях
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users(
    ID INT,
    Company TEXT,
    Center TEXT,
    Section TEXT,
    Name TEXT,
    Surname TEXT,
    Mail TEXT,
    Count INT);
    """
    )
    # 2) создание таблицы названий компаний
    cur.execute(
        """CREATE TABLE IF NOT EXISTS companies(
    ID INT,
    Name TEXT,
    Key TEXT);
    """
    )
    # 3) создание таблицы названий компаний
    cur.execute(
        """CREATE TABLE IF NOT EXISTS centers(
    ID INT,
    Name TEXT,
    Company_id TEXT,
    Key TEXT);
    """
    )
    # 4) создание таблицы названий отделов
    cur.execute(
        """CREATE TABLE IF NOT EXISTS sections(
    ID INT,
    Name TEXT,
    Center_id TEXT,
    Key TEXT);
    """
    )
    # 5) создание таблицы вопросов
    cur.execute(
        """CREATE TABLE IF NOT EXISTS questions(
    ID INT,
    Name TEXT,
    Section_id TEXT,
    Key TEXT);
    """
    )
    # 6) создание тадлицы ответов на вопросы
    cur.execute(
        """CREATE TABLE IF NOT EXISTS answers(
    ID INT,
    Name TEXT,
    Question_id TEXT,
    Key TEXT);
    """
    )
    db.commit()


#
def show_me(table_name):
    cur.execute(f"SELECT Name FROM {table_name}")
    name_lists = list(map(list, cur.fetchall()))
    name = list(chain.from_iterable(name_lists))
    cur.execute(f"SELECT Key FROM {table_name}")
    key_lists = list(map(list, cur.fetchall()))
    key = list(chain.from_iterable(key_lists))
    dictionary = dict(zip(key, name))
    return dictionary


def show_answer(key):
    info = cur.execute('SELECT Name FROM answers WHERE Key = ?', (key, ))
    return str(info.fetchone())[2:-3]


# Функция добавления данных в таблицу
async def add_data(state):
    async with state.proxy() as data:
        cur.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", tuple(data.values())
        )
    db.commit()


# Функция удаления данных (Нужна, если 3 попытки ввода кода провалились)
async def del_data(USER_ID):
    cur.execute('DELETE FROM users WHERE ID = ?', (USER_ID, ))
    db.commit()


# Прибавление значений к счетчику
def add_count(count, USER_ID):
    cur.execute("UPDATE users SET Count = Count + ? WHERE ID = ?", (count, USER_ID))
    db.commit()


def return_section(USER_ID):
    info = cur.execute('SELECT Section FROM users WHERE ID = ?', (USER_ID, ))
    return str(info.fetchone())[2:-3]


# Счетчик неправильных попыток
def check(USER_ID):
    info = cur.execute('SELECT Count FROM users WHERE ID = ?', (USER_ID, ))
    db.commit()
    res = sum(info.fetchone())
    if res >= 3:
        return True


# Проверка на наличие пользователя в бд
def valid_id(USER_ID):
    info = cur.execute('SELECT EXISTS(SELECT ID FROM users WHERE ID = ?)', (USER_ID, ))
    db.commit()
    res = sum(info.fetchone())
    return res
