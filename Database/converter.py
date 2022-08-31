import sqlite3

import pandas as pd  # pip install pandas

conn = sqlite3.connect(
    "C:/Users/arsen/PycharmProjects/Volna_telegram_bot/telegram_bot.db"
)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cur.fetchall())
table = input("Введите нужную таблицу: ")
df = pd.read_sql(f"select * from {table}", conn)
df.to_excel(
    r"C:/Users/arsen/PycharmProjects//Volna_telegram_bot/Database/result.xlsx",
    index=False,
)
