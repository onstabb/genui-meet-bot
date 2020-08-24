from aiogram import types


async def search(prof_id):
    key = types.InlineKeyboardMarkup()
    if prof_id:
        key.add(types.InlineKeyboardButton(text='Нравится', callback_data=f'like {prof_id}'),
                types.InlineKeyboardButton(text='Не нравится', callback_data=f'pass {prof_id}'))
        # key.add(types.InlineKeyboardButton(text='Пожаловаться на анкету', callback_data=f'repo {prof_id}'))
        key.add(types.InlineKeyboardButton(text='Нравится, оставить письмо', callback_data=f'send {prof_id}'))
        key.add(types.InlineKeyboardButton(text='Не хочу больше оценивать', callback_data=f'back'))
    else:
        key.add(types.InlineKeyboardButton(text='Вернуться обратно', callback_data=f'back'))
    return key


async def profile_status(c_data):
    key = types.InlineKeyboardMarkup()
    if c_data == 'like':
        text = 'Нравится! Ждём ответа'
    elif c_data == 'back':
        text = "Будем ждать заявок"
    elif c_data == 'sent':
        text = 'Отправлено сообщение!'
    else:
        text = 'Пропускаем...'

    key.add(types.InlineKeyboardButton(text=text, callback_data='watched'))
    return key


async def profile_income_status(c_data):
    key = types.InlineKeyboardMarkup()
    text = 'Есть взаимность!' if c_data == 'yess' else 'Пропускаем'
    key.add(types.InlineKeyboardButton(text=text, callback_data='watched'))
    return key


async def liked(profile_id, with_message: bool = False):
    key = types.InlineKeyboardMarkup()
    data = 'seen' if with_message is False else 'mess'
    key.add(types.InlineKeyboardButton(text="Посмотреть анкету", callback_data=f'{data} {profile_id}'))
    return key


async def profile_income(prof_id):
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(text='Нравится', callback_data=f'yess {prof_id}'),
            types.InlineKeyboardButton(text='Не нравится', callback_data=f'nope {prof_id}'))
    # key.add(types.InlineKeyboardButton(text='Пожаловаться на анкету', callback_data=f'repor{prof_id}'))
    return key
