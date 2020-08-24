from aiogram import Bot, Dispatcher
import logging
import config
import os
from aiogram.contrib.fsm_storage.mongo import MongoStorage

bot = Bot(config.TOKEN)
MongoDB = MongoStorage(host=config.Mongo.host, port=config.Mongo.port + '/' + config.Mongo.db_name,
                       username=config.Mongo.username, password=config.Mongo.password, db_name=config.Mongo.db_name)

income_picture = os.environ.get('INCOME_PICTURE')\
    if os.environ.get('INCOME_PICTURE') is not None else \
    "AgACAgIAAxkDAAIHA17P-qCE0MRFPOhKAlDDl8fzEO_jAAK1rjEb-xKBSq8q47TF4U5XKYNvkS4AAwEAAwIAA3gAA-HPAwABGQQ"


async def get_inc_pic():
    with open('resources/income_profile.png', 'rb') as ph:
        a = await bot.send_photo(config.admins['main'], ph)
        return a['photo'][1]['file_id']


dp = Dispatcher(bot, storage=MongoDB)
logging.basicConfig(level=logging.INFO)
