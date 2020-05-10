from aiogram import Bot, Dispatcher
import logging
import config
from geopy.geocoders import Nominatim
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


geo = Nominatim(user_agent=config.USER_AGENT, timeout=3)
bot = Bot(config.TOKEN)
memory_storage = MemoryStorage()
dp = Dispatcher(bot, storage=memory_storage)
logging.basicConfig(level=logging.INFO)


async def begin(*args):
    await bot.send_message(config.admins[0], 'Запустился!')


class Profile(StatesGroup):
    make = State()
    name = State()
    sex = State()
    age = State()
    city = State()
    search = State()
    photo = State()
    desc = State()


async def detecting_city(city: str = None, location: tuple = None):
    loc = None

    if city is not None:
        loc = geo.geocode(city, addressdetails=True, language='ru')

    elif location is not None:
        loc = geo.reverse(location, addressdetails=True, language='ru')

    if loc is None:
        return None
    address = loc.raw['address']
    if address.get('city') is None:
        if address.get('town') is None:
            if address.get('city_district') is None:
                if address.get('county') is None:
                    if address.get('state') is not None:
                        city = address['state']
                else:
                    city = address['county']
            else:
                city = address['city_district']
        else:
            city = address['town']
    else:
        city = address['city']

    return city, address['state'], address['country'], (loc.latitude, loc.longitude)
