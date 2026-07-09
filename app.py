import asyncio
import logging
import sys
from handlers import*
from loader import bot, dp, storage
from utils.bot_commands import set_commands
from utils.notify_admins import notify_bot_admins
logger = logging.getLogger(__name__)


from loader import pyro

async def main():
    await pyro.start()
    await set_commands()
    await notify_bot_admins()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await pyro.stop()
        await storage.close()
        await bot.session.close()

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass