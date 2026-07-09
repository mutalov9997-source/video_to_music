from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from telethon import TelegramClient
from telethon.sessions import StringSession
from data import BOT_TOKEN, REDIS_HOST, USE_REDIS, API_ID, API_HASH, SESSION_STRING

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

storage = RedisStorage.from_url(f"redis://{REDIS_HOST}") if USE_REDIS else MemoryStorage()
dp = Dispatcher(storage=storage)

pyro = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)