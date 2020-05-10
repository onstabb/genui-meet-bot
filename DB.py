import asyncpg
import asyncio
import config



async def connect(dsn: str = config.URL):
    conn = await asyncpg.connect(dsn=dsn)
    return conn


async def create_table():
    conn = await connect()
    await conn.execute("""CREATE TABLE IF NOT EXISTS users (
    id serial PRIMARY KEY,
    chat_id INT NOT NULL UNIQUE,
    registered timestamp NOT NULL,
    name text,
    sex text,
    age int,
    city text,
    state text,
    country text,
    coordinates tid,
    search text,
    photo_id text,
    active bool NOT NULL DEFAULT false,
    blocked bool NOT NULL DEFAULT false,)
    """)
    await conn.close()


async def show_all():
    conn = await connect()
    show = await conn.fetch("SELECT * FROM users")
    await conn.close()
    for i in show:
        show[show.index(i)] = dict(i)
    return show


async def check_new_user(chat_id: int, datetime):
    conn = await connect()
    show = await conn.fetch("SELECT chat_id FROM users")
    for i in show:
        show[show.index(i)] = tuple(i)[0]
    x = False

    if chat_id not in show:
        await conn.execute("""INSERT INTO users(chat_id, registered) VALUES ($1, $2)""", chat_id, datetime)
        x = True

    await conn.close()
    return x


async def user_info(chat_id):
    conn = await connect()
    show = await conn.fetchrow(f"SELECT * FROM users WHERE chat_id = {chat_id}")
    await conn.close()
    return show


async def delete_profile(chat_id):
    conn = await connect()
    await conn.execute(
        f"UPDATE users "
        f"SET name = null, sex = null, age = null, city = null, state = null, search = null, photo_id = null, "
        f"description = null, active = false "
        f"WHERE chat_id = {chat_id}")
    await conn.close()


async def add_user_info(chat_id: int, info: str, value):
    conn = await connect()
    await conn.execute(f"UPDATE users SET {info} = '{value}' WHERE chat_id = {chat_id}")
    await conn.close()


async def add_location(chat_id: int, address: tuple):
    city = address[0]
    state = address[1]
    country = address[2]
    coordinates = f"{address[3][0]}, {address[3][1]}"
    conn = await connect()
    await conn.execute(
        f"UPDATE users SET city = '{city}', state = '{state}', country = '{country}', coordinates = '{coordinates}' "
        f"WHERE chat_id = {chat_id}")
    await conn.close()

if __name__ == '__main__':
    print(asyncio.get_event_loop().run_until_complete(user_info(182694754)))
