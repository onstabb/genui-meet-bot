import config


class Dice:
    marked = "=" * 15
    more = 'Бросай еще!'


async def profile(record, admin):
    if record:
        data = dict(record)
        prof = f"{data['name']}, {data['age']}, {data['city']}\n\n" \
               f"{data['description']}"
        if admin == config.admins['main']:
            prof += f"\n\nНомер анкеты: {data['id']}\nЧат ID: {data['chat_id']}"

        return prof
    else:
        return 'Прости, но я сейчас не нашёл для тебя подходящий профиль... Но это лишь вопрос времени. ' \
               'Думаю, скоро кто-то еще появится.\nА пока не забудь рассказать друзьям о боте!'
