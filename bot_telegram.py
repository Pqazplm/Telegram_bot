from aiogram.utils import executor

from bot_telegram_create import dp
from Database import db_telegram_bot as db
from handlers import bot_telegram_admin, bot_telegram_client, bot_telegram_other


async def on_startup(_):
    print("Бот вышел в онлайн")
    db.db_start()


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
