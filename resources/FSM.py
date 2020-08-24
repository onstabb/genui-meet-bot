from aiogram.dispatcher.filters.state import State, StatesGroup


class Profile(StatesGroup):
    make = State()
    name = State()
    sex = State()
    age = State()
    city = State()
    search = State()
    photo = State()
    desc = State()

    active = State()
    switch_active = State()
    like_message = State()
    support = State()
