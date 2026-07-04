from data import ADMINS
from loader import bot


async def notify_bot_admins():

    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=admin, text="Bot ishga tushdi!")
        except Exception as err:
            pass