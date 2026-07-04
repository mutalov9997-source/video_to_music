from environs import Env

env = Env()

env.read_env()

ADMINS = env.list('ADMINS')
BOT_TOKEN = env.str('BOT_TOKEN')

USE_REDIS = env.bool('USE_REDIS')
REDIS_HOST = env.str('REDIS_HOST')