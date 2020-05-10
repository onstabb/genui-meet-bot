from aiogram import types
from misc import dp, Profile, detecting_city
import asyncio
import DB
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands='start')
async def start(message: types.Message):
    if await DB.check_new_user(message.chat.id, message.date) is True:
        await message.answer('Приветствую тебя на моей площадке знакомств! Я Дженью бот!')
        await asyncio.sleep(3)
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Заполнить анкету')
        await message.answer("Для начала тебе необходимо заполнить анкету.", reply_markup=key)

    else:
        await message.answer('Привет тебе снова!')


@dp.message_handler(commands=['profile', 'refresh'])
async def main(message: types.Message):
    profile = await DB.user_info(message.chat.id)
    if None in tuple(profile):
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Заполнить анкету')
        await message.answer('У тебя не заполнена анкета! Чтобы заполнить данные, введи команду /refill, '
                             'либо жми на кнопку внизу', reply_markup=key)
    else:
        await message.answer_photo(
            f"{dict(profile)['photo_id']}",
            caption=f"{dict(profile)['name']}, {dict(profile)['age']}, {dict(profile)['city']}\n"
                    f"{dict(profile)['description']}\n\nЭто твой профиль.")


@dp.message_handler(commands=['refill', 'delprofile'], state='*')
@dp.message_handler(lambda message: message.text == 'Заполнить анкету')
async def make_profile(message: types.Message, state: FSMContext):
    record = await DB.user_info(message.chat.id)
    if message.text == '/delprofile':
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Да', 'Нет')
        await Profile.make.set()
        return await message.answer('Хочешь заново заполнить профиль?', reply_markup=key)

    if None in tuple(record):
        if dict(record)['name'] is None:
            await Profile.name.set()
            await message.answer("Окей, как тебя зовут?", reply_markup=types.ReplyKeyboardRemove())
        elif dict(record)['sex'] is None:
            key = types.ReplyKeyboardMarkup(resize_keyboard=True)
            key.add('Я парень', 'Я девушка')
            await Profile.sex.set()
            await message.answer(f"Кто ты по полу?", reply_markup=key)
        elif dict(record)['age'] is None:
            await Profile.age.set()
            await message.answer("Сколько тебе лет?", reply_markup=types.ReplyKeyboardRemove())
        elif dict(record)['city'] is None:
            await Profile.city.set()
            await message.answer("Из какого ты города?\nА лучше пришли свои координаты!")
        elif dict(record)['search'] is None:
            key = types.ReplyKeyboardMarkup(resize_keyboard=True)
            key.add('Парня', 'Девушку', 'Всё равно')
            await Profile.search.set()
            await message.answer("Кого бы ты хотел найти?", reply_markup=key)
        elif dict(record)['photo_id'] is None:
            await Profile.photo.set()
            await message.answer("Отправляй свою фотографию для анкеты.",
                                 reply_markup=types.ReplyKeyboardRemove())
        elif dict(record)['description'] is None:
            await Profile.desc.set()
            await message.answer("Напиши что-нибудь о себе, чем бы хотел занятся, кого ищешь и т.д.")
    else:
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Да', 'Нет')
        await Profile.make.set()
        return await message.answer('Хочешь заново заполнить профиль?', reply_markup=key)


@dp.message_handler(state=Profile.name, content_types=['text'])
async def set_name(message: types.Message, state: FSMContext):
    if message.text.isalpha():
        await DB.add_user_info(message.chat.id, "name", message.text)
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Я парень', 'Я девушка')
        await Profile.sex.set()
        await message.answer(f"Очень приятно, {message.text}!\nКто ты по полу?", reply_markup=key)
    else:
        await message.answer("Какое-то странно имя... Попробуй ввести ещё раз.")


@dp.message_handler(state=Profile.sex, content_types=['text'])
async def set_sex(message: types.Message, state: FSMContext):
    if message.text == "Я парень":
        sex = 'мужской'
    elif message.text == "Я девушка":
        sex = 'женский'
    else:
        return message.answer("Прости, но я не понял тебя.\nВведи соответствующую кнопку внизу для ответа")

    await DB.add_user_info(message.chat.id, "sex", sex)
    await Profile.age.set()
    await message.answer("Сколько тебе лет?", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Profile.age, content_types=['text'])
async def set_age(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        age = int(message.text)
        if age >= 75:
            await message.answer('Что-то я тебе не верю. Введи корректный возраст!')
        elif age < 13:
            await message.answer('Такой возраст я не принимаю!')
        else:
            await Profile.city.set()
            await DB.add_user_info(message.chat.id, "age", age)
            await message.answer('Из какого ты города?')
    else:
        await message.answer('Введи свой возраст цифрой!')


@dp.message_handler(state=Profile.city, content_types=['text', 'location'])
async def set_city(message, state: FSMContext):
    address = None
    if message.text:
        try:
            address = await detecting_city(city=message.text)
        except Exception:
            return await message.answer('Что-то пошло не так, попробуй ещё раз!')

    elif message.location:
        coordinates = message.location.latitude, message.location.longitude
        try:
            address = await detecting_city(location=coordinates)
        except Exception:
            return await message.answer('Что-то пошло не так, попробуй ещё раз!')
    if address is None:
        return await message.answer('Не получилось определить город, попробуй ещё раз!')

    await DB.add_location(message.chat.id, address=address)
    await Profile.search.set()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add('Парня', 'Девушку', 'Всё равно')
    await message.answer(f'Я определил твой город для себя как {address[0]}.\n'
                         f'Если я неверно определил, то напиши по обратной связи моим создателям отчёт об ошибке!\n'
                         f'А пока продолжим:\n\nКого тебе искать?', reply_markup=key)


@dp.message_handler(state=Profile.search, content_types=['text'])
async def set_search(message: types.Message, state: FSMContext):
    if message.text == 'Парня':
        search = 'мужской'
    elif message.text == 'Девушку':
        search = 'женский'
    elif message.text == 'Всё равно':
        search = 'любой'
    else:
        return message.answer('Не понял, так кого бы ты хотел найти?')

    await Profile.photo.set()
    await DB.add_user_info(message.chat.id, "search", search)
    await message.answer('Отправляй свою фотографию, '
                         'которая будет у тебя в анкете.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Profile.photo, content_types=['photo'])
async def set_photo(message, state: FSMContext):
    await DB.add_user_info(message.chat.id, 'photo_id', message['photo'][1]['file_id'])
    await Profile.desc.set()
    await message.answer("Напиши что-нибудь о себе, чем бы хотел занятся, кого ищешь и т.д.")


@dp.message_handler(state=Profile.desc, content_types=['text'])
async def set_description(message: types.Message, state: FSMContext):
    await DB.add_user_info(message.chat.id, 'description', message.text)
    await DB.add_user_info(message.chat.id, 'active', True)
    await state.finish()
    await message.answer("Что ж, ты заполнил все данные...")
    await asyncio.sleep(3)
    await main(message)


@dp.message_handler(state=Profile.make)
async def fill_profile(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        await DB.delete_profile(message.chat.id)
        await Profile.name.set()
        await make_profile(message, state)
    elif message.text == 'Нет':
        await message.answer('Назад...', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await asyncio.sleep(1)
        await main(message)


@dp.message_handler(content_types=['dice'])
async def messages(message):
    dice = await message.answer_dice(message.dice.emoji)
    await asyncio.sleep(5)
    if dice.dice.value > message.dice.value:
        await message.answer('Моя взяла!')
    elif dice.dice.value == message.dice.value:
        await message.answer('Ну ничья.')
    else:
        await message.answer('Ты выиграл!')

