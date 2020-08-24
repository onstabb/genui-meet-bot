from aiogram import types
from misc import dp, MongoDB, bot, income_picture
from resources import KEY, TEXTS
from resources.FSM import Profile
from resources.geores import detecting_city
import asyncio
from DB import PG
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest
from config import admins


@dp.message_handler(commands='start', state='*')
async def start(message: types.Message):
    if await PG.check_new_user(message.chat.id, message.date) is True:
        await message.answer('Приветствую тебя на моей площадке знакомств! Я Роботизированный Беня, '
                             'или просто Беня Бот.\n'
                             'И я могу помочь тебе найти новые знакомства!')
        await asyncio.sleep(3)
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Заполнить анкету')
        await message.answer("Для начала тебе необходимо заполнить анкету, а также необходимо иметь "
                             "ссылку на свой профиль Telegram в виде @username. Её ты можешь сделать в настройках",
                             reply_markup=key)
    else:
        await message.answer('Привет тебе снова!')
        await asyncio.sleep(1)
        await default_handler(message)


@dp.message_handler(state='*', commands=['profile', 'refresh'])
async def profile(message: types.Message):

    my_profile = await PG.user_info(message.chat.id)
    if None in tuple(my_profile) or dict(my_profile)['active'] is False or not message.chat.username:
        await default_handler(message)
    else:

        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Смотреть анкеты', 'Заполнить заного')
        key.add('Отключить анкету', 'Обратная связь')
        await Profile.active.set()
        await message.answer_photo(
            f"{dict(my_profile)['photo_id']}",
            caption=await TEXTS.profile(my_profile, message.chat.id) + "\n\n\nЭто твой профиль", reply_markup=key)


@dp.message_handler(state='*', commands=['support'])
async def support(message: types.Message):
    await Profile.support.set()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add('Вернуться')
    await message.answer('Здесь ты можешь написать моим создателям в качестве обратной связи. '
                         'Ты можешь задавать свои вопросы, рассказать об ошибках, глюках, пожаловаться, '
                         'отправлять пожелания, скрины и фото.\n'
                         'Присылай все сообщения и содержимое прямо здесь. Я всё передам!\n\n'
                         'Чтобы выйти нажми кнопку "Вернуться" внизу.', reply_markup=key)


@dp.message_handler(state='*', commands=['profileform', 'refill'], content_types='text')
async def make_profile(message: types.Message):
    record = await PG.user_info(message.chat.id)

    if message.text == '/refill':
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
            await message.answer(f"Твой пол?", reply_markup=key)
        elif dict(record)['age'] is None:
            await Profile.age.set()
            await message.answer("Сколько тебе лет?", reply_markup=types.ReplyKeyboardRemove())
        elif dict(record)['city'] is None:
            await Profile.city.set()
            await message.answer("Из какого ты города?\nА лучше пришли своё местоположение!")
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


@dp.message_handler(state=Profile.active, commands=['deactivating'])
async def deactivated(message: types.Message):
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add('Да', 'Нет')
    await message.answer('Ты действительно хочешь отключить анкету?', reply_markup=key)
    await Profile.switch_active.set()


@dp.message_handler(state=Profile.active)
async def main(message: types.Message, state: FSMContext):
    if message.text == 'Смотреть анкеты':
        await message.answer('Ну что ж, посмотрим...', reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        prof = await PG.search_profile(message.chat.id, await MongoDB.get_bucket(chat=message.chat.id))
        if prof:
            prof_id = str(dict(prof)['id'])
            await state.update_data(watched_profile=prof_id)
            await message.answer_photo(f"{dict(prof)['photo_id']}",
                                       caption=await TEXTS.profile(prof, message.chat.id),
                                       reply_markup=await KEY.search(prof_id))
        else:
            await state.reset_data()
            await MongoDB.set_bucket(chat=message.chat.id, bucket={})
            await message.answer(await TEXTS.profile(prof, message.chat.id), reply_markup=await KEY.search(prof))
    elif message.text == 'Моя анкета':
        await profile(message)
    elif message.text == 'Обратная связь':
        await support(message)
    elif message.text == 'Отключить анкету':
        await deactivated(message)
    elif message.text in ['Заполнить анкету', 'Заполнить заного']:
        await make_profile(message)


@dp.callback_query_handler(state=Profile.active)
async def searching(c: types.CallbackQuery, state: FSMContext):
    data_comm = c.data[:4]
    data_prof = c.data[5:]
    if data_comm == 'like' or data_comm == 'pass':
        if data_comm == "like":
            # check @user
            if not c.message.chat.username:
                return await c.message.edit_text('У тебя нет @username!', reply_markup=await KEY.search(None))

            get_profile = dict(await PG.user_info_by_id(data_prof))
            my_profile = dict(await PG.user_info(c.message.chat.id))
            await MongoDB.update_bucket(chat=get_profile['chat_id'], bucket={str(my_profile["id"]): "liked"})

            await bot.send_photo(get_profile['chat_id'], photo=income_picture,
                                 caption="Кажется ты кому-то нравишься!\n"
                                         "Чтобы узнать кому, открой анкету по кнопке внизу:",
                                 reply_markup=await KEY.liked(str(my_profile['id'])))

        await MongoDB.update_bucket(bucket={data_prof: data_comm}, chat=c.message.chat.id)
        await c.message.edit_reply_markup(reply_markup=await KEY.profile_status(data_comm))

        prof = await PG.search_profile(c.message.chat.id, await MongoDB.get_bucket(chat=c.message.chat.id))
        await asyncio.sleep(1)
        if prof:
            prof_id = str(dict(prof)['id'])

            await state.update_data(watched_profile=prof_id)
            await c.message.answer_photo(f"{dict(prof)['photo_id']}",
                                         caption=await TEXTS.profile(prof, c.message.chat.id),
                                         reply_markup=await KEY.search(prof_id))
        else:
            await state.reset_data()
            await MongoDB.set_bucket(chat=c.message.chat.id, bucket={})
            await c.message.answer(await TEXTS.profile(prof, c.message.chat.id), reply_markup=await KEY.search(prof))

    elif data_comm == 'seen' or data_comm == 'mess':
        if not c.message.chat.username:
            return await c.message.edit_caption(
                'У тебя нет ссылки @username! Чтобы открыть профиль, тебе необходимо иметь'
                ' эту ссылку. Её можно сделать в настройках профиля Telegram.',
                reply_markup=await KEY.liked(data_prof))

        mes_for_you = ''

        get_profile = await PG.user_info_by_id(data_prof)
        await asyncio.sleep(1)

        if data_comm == 'mess':
            bucket = await MongoDB.get_bucket(chat=c.message.chat.id)
            mes_for_you = f'\n\nСообщение для тебя: {bucket[data_prof]}'

        media = types.InputMediaPhoto(dict(get_profile)['photo_id'],
                                      caption=await TEXTS.profile(get_profile, c.message.chat.id) + mes_for_you)
        await c.message.edit_media(media, reply_markup=await KEY.profile_income(data_prof))

    elif data_comm == "send":
        await c.message.edit_caption(
            'Введи сообщение которое ты хочешь отправить.\nМаксимальная длина сообщения - 200.')
        await Profile.like_message.set()

    elif data_comm == 'yess' or data_comm == 'nope':
        await c.message.edit_reply_markup(reply_markup=await KEY.profile_income_status(data_comm))

        if data_comm == 'yess':
            get_profile = await PG.user_info_by_id(data_prof)
            get_chat_tg = await bot.get_chat(dict(get_profile)['chat_id'])
            await asyncio.sleep(1)

            if not get_chat_tg.username:
                return await c.message.answer('Хм... Прости, но у юзера отсутствует @username. Он будет наказан!')

            prof = await PG.user_info(c.message.chat.id)
            await bot.send_photo(dict(get_profile)['chat_id'], photo=dict(prof)['photo_id'],
                                 caption=await TEXTS.profile(prof, c.message.chat.id) +
                                         f"\n\nЕсть взаимность! Добавляй: @{c.message.chat.username}")
            await c.message.edit_caption(await TEXTS.profile(get_profile, c.message.chat.id) +
                                         f'\n\nДобавляй: @{get_chat_tg.username}')

    elif data_comm == 'back':
        try:
            await c.message.edit_text('А пока...')
        except BadRequest:
            await c.message.edit_reply_markup(reply_markup=await KEY.profile_status(data_comm))

        await asyncio.sleep(1)
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Моя анкета')
        await c.message.answer('Подождем, пока кто-нибудь увидит твою анкету...', reply_markup=key)


@dp.message_handler(state=Profile.like_message, content_types=['text'])
async def send_message(message: types.Message, state: FSMContext):
    if not message.chat.username:
        return await message.answer('У тебя нет @username!', reply_markup=await KEY.search(None))

    data = await state.get_data('watched_profile')
    get_profile = await PG.user_info_by_id(data['watched_profile'])
    my_profile = await PG.user_info(message.chat.id)
    await bot.send_photo(get_profile['chat_id'], photo=income_picture,
                         caption="Кажется ты кому-то нравишься!\nЧтобы узнать кому, открой анкету по кнопке внизу:",
                         reply_markup=await KEY.liked(str(dict(my_profile)['id']), with_message=True))

    await MongoDB.update_bucket(chat=dict(get_profile)['chat_id'], bucket={str(dict(my_profile)["id"]): message.text})
    await MongoDB.update_bucket(bucket={data['watched_profile']: 'like'}, chat=message.chat.id)

    await Profile.active.set()
    await message.answer_photo(caption=await TEXTS.profile(get_profile, message.chat.id),
                               reply_markup=await KEY.profile_status('sent'), photo=dict(get_profile)['photo_id'])

    prof = await PG.search_profile(message.chat.id, await MongoDB.get_bucket(chat=message.chat.id))
    await asyncio.sleep(2)
    if prof:
        prof_id = str(dict(prof)['id'])

        await state.update_data(watched_profile=prof_id)
        await message.answer_photo(f"{dict(prof)['photo_id']}",
                                   caption=await TEXTS.profile(prof, message.chat.id),
                                   reply_markup=await KEY.search(prof_id))
    else:
        await state.reset_data()
        await MongoDB.set_bucket(chat=message.chat.id, bucket={})
        await message.answer(await TEXTS.profile(prof, message.chat.id), reply_markup=await KEY.search(prof))


@dp.message_handler(state=Profile.switch_active, content_types=['text'])
async def switch_active(message: types.Message, state: FSMContext):
    pfl = await PG.user_info(message.chat.id)

    if message.text == 'Да':
        if dict(pfl)['active'] is False:
            await PG.add_user_info(message.chat.id, 'active', True)
            await Profile.active.set()
            await message.answer('С возвращением! Вот твоя анкета:', reply_markup=types.ReplyKeyboardRemove())
            await asyncio.sleep(1)
            await profile(message)

        else:
            await message.answer('Что ж, до скорого времени! Заходи если что.',
                                 reply_markup=types.ReplyKeyboardRemove())
            await PG.add_user_info(message.chat.id, 'active', False)
            await state.finish()
            await state.reset_data()
            await MongoDB.set_bucket(chat=message.chat.id, bucket={})

    elif message.text == 'Нет':
        if dict(pfl)['active'] is False:
            await message.answer('Мы тебе всегда здесь рады!', reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
        else:
            await Profile.active.set()
            await profile(message)


@dp.message_handler(state=Profile.support, content_types=['text', 'photo'])
async def support_handler(message):
    who = f"Пришло от {message.chat.first_name}, id {message.chat.id}:\n\n"
    if message.photo:
        await bot.send_photo(admins['main'], message['photo'][1]['file_id'], caption=who)
        await message.answer("Передал фото")
    elif message.text:
        if message.text == 'Вернуться':
            await profile(message)
        else:
            await bot.send_message(admins['main'], who + message.text)
            await message.answer("Передал сообщение")


@dp.message_handler(state=Profile.name, content_types=['text'])
async def set_name(message: types.Message):
    if message.text.isalpha():
        await PG.add_user_info(message.chat.id, "name", message.text)
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Я парень', 'Я девушка')
        await Profile.sex.set()
        await message.answer(f"Очень приятно, {message.text}!\nТвой пол?", reply_markup=key)
    else:
        await message.answer("Какое-то странно имя... Попробуй ввести ещё раз.")


@dp.message_handler(state=Profile.sex, content_types=['text'])
async def set_sex(message: types.Message):
    if message.text == "Я парень":
        sex = 'мужской'
    elif message.text == "Я девушка":
        sex = 'женский'
    else:
        return message.answer("Прости, но я не понял тебя.\nВведи соответствующую кнопку внизу для ответа")

    await PG.add_user_info(message.chat.id, "sex", sex)
    await Profile.age.set()
    await message.answer("Сколько тебе лет?", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Profile.age, content_types=['text'])
async def set_age(message: types.Message):
    if message.text.isdigit():
        age = int(message.text)
        if age >= 75:
            await message.answer('Что-то я тебе не верю. Введи корректный возраст!')
        elif age < 13:
            await message.answer('Такой возраст я не принимаю!')
        else:
            await Profile.city.set()
            await PG.add_user_info(message.chat.id, "age", age)
            await message.answer('Из какого ты города? А лучше пришли своё местоположение!')
    else:
        await message.answer('Введи свой возраст цифрой!')


@dp.message_handler(state=Profile.city, content_types=['text', 'location'])
async def set_city(message):
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

    await PG.add_location(message.chat.id, address=address)
    await Profile.search.set()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add('Парня', 'Девушку', 'Всё равно')
    await message.answer(f'В моём глобусе твой регион обозначен как г. {address[0]}, {address[2]}\n'
                         f'Если неверно определено, то сообщи об этом моим создателям! '
                         f'В любом случае, я буду искать людей ближе к твоему присланному местоположению.\n'
                         f'А пока продолжим:\n\nКого тебе искать?', reply_markup=key)


@dp.message_handler(state=Profile.search, content_types=['text'])
async def set_search(message: types.Message):
    if message.text == 'Парня':
        search = 'мужской'
    elif message.text == 'Девушку':
        search = 'женский'
    elif message.text == 'Всё равно':
        search = 'любой'
    else:
        return message.answer('Не понял, так кого бы ты хотел найти?')

    await Profile.photo.set()
    await PG.add_user_info(message.chat.id, "search", search)
    await message.answer('Отправляй свою фотографию, '
                         'которая будет у тебя в анкете.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Profile.photo, content_types=['photo'])
async def set_photo(message):
    await PG.add_user_info(message.chat.id, 'photo_id', message['photo'][1]['file_id'])
    await Profile.desc.set()
    await message.answer("Напиши что-нибудь о себе, чем бы хотел занятся, кого ищешь и т.д.")


@dp.message_handler(state=Profile.desc, content_types=['text'])
async def set_description(message: types.Message):
    if len(message.text) <= 750:
        await PG.add_user_info(message.chat.id, 'description', message.text)
        await PG.add_user_info(message.chat.id, 'active', True)
        await Profile.active.set()
        await message.answer("Что ж, ты заполнил все данные...\n"
                             "Твоя анкета активирована!\n\nВот она:")
        await asyncio.sleep(3)
        await profile(message)
    else:
        await message.answer('Слишком большой текст!\nНельзя больше 900-та символов.')


@dp.message_handler(state=Profile.make)
async def fill_profile(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        await PG.delete_profile(message.chat.id)
        await state.finish()
        await state.reset_data()
        await MongoDB.set_bucket(chat=message.chat.id, bucket={})
        await Profile.name.set()
        await make_profile(message)
    elif message.text == 'Нет':
        await message.answer('Назад...', reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        await profile(message)


@dp.message_handler(content_types=['text'], state='*')
async def default_handler(message: types.Message):
    profile = await PG.user_info(message.chat.id)
    if not message.chat.username:
        return await message.answer('У тебя отсутствует @username ссылка! Для того, чтобы ты можно было узнать'
                                    ' кому ты нравишься, необходима публичная ссылка @username в твоем '
                                    'Telegram профиле. Её можно сделать в настройках.')

    if None in tuple(profile):
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Заполнить анкету')
        return await message.answer('У тебя не заполнена анкета! Чтобы заполнить данные, введи команду /profileform, '
                                    'либо жми на кнопку внизу', reply_markup=key)

    if dict(profile)['active'] is False:
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.add('Да', 'Нет')

        await Profile.switch_active.set()
        return await message.answer('Хочешь снова включить анкету?', reply_markup=key)


@dp.message_handler(content_types=['dice'], state='*')
async def messages(message):
    dice = await message.answer_dice(message.dice.emoji)
    await asyncio.sleep(5)
    if dice.dice.value > message.dice.value:
        await message.answer(f'Я выиграл!\n{TEXTS.Dice.marked}\n'
                             f'Твой результат: {message.dice.value}\n'
                             f'Мой: {dice.dice.value}\n{TEXTS.Dice.marked}\n' + TEXTS.Dice.more)

    elif dice.dice.value == message.dice.value:
        await message.answer(f'Ну ничья.\n{TEXTS.Dice.marked}\n'
                             f'Твой результат: {message.dice.value}\n'
                             f'Мой: {dice.dice.value}\n{TEXTS.Dice.marked}\n' + TEXTS.Dice.more)
    else:
        await message.answer(f'Твоя взяла!\n'
                             f'{TEXTS.Dice.marked}\n'
                             f'Твой результат: {message.dice.value}\n'
                             f'Мой: {dice.dice.value}\n'
                             f'{TEXTS.Dice.marked}\n' + TEXTS.Dice.more)