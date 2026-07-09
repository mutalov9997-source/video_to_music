from environs import Env

env = Env()

env.read_env()

ADMINS = env.list('ADMINS')
BOT_TOKEN = env.str('BOT_TOKEN')
API_ID = env.int('API_ID')
API_HASH = env.str('API_HASH')
USE_REDIS = env.bool('USE_REDIS')
REDIS_HOST = env.str('REDIS_HOST')