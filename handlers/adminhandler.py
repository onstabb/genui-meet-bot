from misc import dp, bot
from aiogram import types
import config


@dp.message_handler(lambda message: message.chat.id in config.admins, commands='set_commands')
async def cmd_set_commands(message: types.Message):
    commands = [types.BotCommand(command="/refresh", description="Обновить бота, если что-то не так, или не то"),
                types.BotCommand(command="/profile", description="Профиль"),
                types.BotCommand(command="/refill", description="Дополнить анкету"),
                types.BotCommand(command="/newprofile", description="Заполнить анкету заново"),
                types.BotCommand(command="/deactivate", description="Отключить анкету")]

    await bot.set_my_commands(commands)
    await message.answer("Команды настроены.")
