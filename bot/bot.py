import os
from os.path import join, abspath
import sys
sys.path.append(join(abspath(".."), 'modelling'))

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.types.update import AllowedUpdates

from config import load_config
from handlers import register_handlers

logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)


def register(dp: Dispatcher):
    register_handlers(dp)


async def main():
    config = load_config(".env")
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    bot['config'] = config
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    register(dp)

    try:
        await dp.start_polling(allowed_updates=AllowedUpdates.MESSAGE + AllowedUpdates.CALLBACK_QUERY)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Stopped.")
