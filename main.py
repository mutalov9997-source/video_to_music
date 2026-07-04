import asyncio
import logging

from app import main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")