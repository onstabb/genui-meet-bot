from misc import dp, bot, MongoDB
from aiogram import types
from DB import PG
import config
from aiogram.dispatcher import FSMContext
from resources import TEXTS


@dp.message_handler(lambda message: message.chat.id == config.admins['main'], commands='set_commands', state="*")
async def cmd_set_commands(message: types.Message):
    commands = [types.BotCommand(command="/refresh", description="Обновить бота, если что-то не так, или не то"),
                types.BotCommand(command="/profile", description="Профиль"),
                types.BotCommand(command="/profileform", description="Дополнить анкету, или заполнить заново"),
                types.BotCommand(command="/refill", description="Заполнить анкету заново"),
                types.BotCommand(command="/deactivating", description="Отключить анкету"),
                types.BotCommand(command="/support", description="Поддержка"), ]

    await bot.set_my_commands(commands)
    await message.answer("Команды настроены.")


@dp.message_handler(lambda message: message.chat.id == config.admins['main'], commands='admin_info', state="*")
async def admin_info(message: types.Message, state: FSMContext):
    await message.answer(await MongoDB.get_bucket(chat=message.chat.id))


@dp.message_handler(lambda message: message.chat.id == config.admins['main'], regexp='(^/pg )', state='*')
async def pg_commands(message: types.Message):
    await message.answer(await PG.exe_command(message.text[4:]))


@dp.message_handler(lambda message: message.chat.id == config.admins['main'], regexp='(^/ans)', state='*')
async def db_commands(message: types.Message):
    # /ans/chat_id/ message
    chat_id = int(message.text.split("/")[2])
    text = message.text.split("/ ")[1]
    await bot.send_message(chat_id, text)
    await message.answer(f"Отправлено к {chat_id}")


@dp.message_handler(lambda message: message.chat.id == config.admins['main'], regexp='(^/showinfo )', state='*')
async def db_info(message: types.Message):
    prof = dict(await PG.user_info_by_id(message.text[10:]))
    await message.answer_photo(f"{prof['photo_id']}",
                               caption=await TEXTS.profile(prof, message.chat.id)+"/n"
                                       + str(await bot.get_chat(prof['chat_id'])))

