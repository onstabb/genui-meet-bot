from aiogram import executor
from misc import dp, begin
import handlers


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=begin)

