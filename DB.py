import asyncpg
import asyncio
import config
from resources.geores import distancing


class Postgres(object):

    def __init__(self, dsn: str = config.URL):
        self._dsn = dsn
        self._conn = None

    async def connect(self):
        if isinstance(self._conn, asyncpg.Connection):

            if self._conn.is_closed():
                self._conn = await asyncpg.connect(dsn=self._dsn)
            return self._conn

        self._conn = await asyncpg.connect(dsn=self._dsn)
        return self._conn

    async def exe_command(self, command: str):
        conn = await self.connect()
        if command.lower().startswith('select'):
            return await conn.fetch(command)
        else:
            return await conn.execute(command)

    async def create_table(self):
        conn = await self.connect()
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
        coordinates text,
        search text,
        photo_id text,
        description text,
        active bool NOT NULL DEFAULT false,
        blocked bool NOT NULL DEFAULT false)
        """)
        await conn.close()

    async def show_all(self):
        conn = await self.connect()
        show = await conn.fetch("SELECT * FROM users")
        for i in show:
            show[show.index(i)] = dict(i)
        return show

    async def check_new_user(self, chat_id: int, datetime):
        conn = await self.connect()
        show = await conn.fetch("SELECT chat_id FROM users")
        for i in show:
            show[show.index(i)] = tuple(i)[0]

        if chat_id not in show:
            await conn.execute("""INSERT INTO users(chat_id, registered) VALUES ($1, $2)""", chat_id, datetime)
            return True
        else:
            return False

    async def user_info(self, chat_id):
        conn = await self.connect()
        show = await conn.fetchrow(f"SELECT * FROM users WHERE chat_id = {chat_id}")
        return show

    async def user_info_by_id(self, profile_id):
        conn = await self.connect()
        profile_id = int(profile_id)
        show = await conn.fetchrow(f"SELECT * FROM users WHERE id = {profile_id}")
        return show

    async def delete_profile(self, chat_id):
        conn = await self.connect()
        await conn.execute(
            f"UPDATE users "
            f"SET name = null, sex = null, age = null, city = null, state = null, search = null, photo_id = null, "
            f"description = null, active = false "
            f"WHERE chat_id = {chat_id}")

    async def add_user_info(self, chat_id: int, info: str, value):
        conn = await self.connect()
        await conn.execute(f"UPDATE users SET {info} = '{value}' WHERE chat_id = {chat_id}")

    async def add_location(self, chat_id: int, address: tuple):
        city = address[0]
        state = address[1]
        country = address[2]
        coordinates = f"{address[3][0]}, {address[3][1]}"
        conn = await self.connect()
        await conn.execute(
            f"UPDATE users SET city = '{city}', state = '{state}', country = '{country}', coordinates = '{coordinates}'"
            f"WHERE chat_id = {chat_id}")

    async def close(self):
        conn = await self.connect()
        if not conn.is_closed():
            await conn.close()

    async def search_profile(self, chat_id, bucket):

        conn = await self.connect()
        user = dict(await conn.fetchrow(f'SELECT * FROM users WHERE chat_id = {chat_id}'))
        passed = list(bucket.keys())
        passed.append(user['id'])
        passed_int = "("
        for i in passed:
            if passed[-1] == i:
                passed_int += f"{i}"
            else:
                passed_int += f"{i}, "
        passed_int += f")"

        boy = 'мужской'
        girl = 'женский'
        if user['active']:
            if user['search'] == 'любой':

                if user['sex'] == girl:
                    do_not_search = boy
                else:
                    do_not_search = girl

                profiles_for_user = await conn.fetch(
                    f'SELECT * FROM users '
                    f'WHERE age >= $1-2 AND age <= $1+2 AND active = true AND search != $2 AND id NOT IN {passed_int}',
                    user['age'], do_not_search
                )
            else:
                # if user['search'] == girl:
                #     do_not_search = boy
                # else:
                #     do_not_search = girl

                profiles_for_user = await conn.fetch(
                    f'SELECT * FROM users '
                    f'WHERE age >= $1-2 AND age <= $1+2 AND search != $2 AND sex = $2 AND active = true AND '
                    f'id NOT IN {passed_int}',
                    user['age'], user['search'],
                )

            # profiles_for_user = list(filter(lambda prof: str(dict(prof)['id']) not in passed, profiles_for_user))

            if profiles_for_user:
                near = min(list(distancing(user['coordinates'], profiles_for_user)), key=lambda prof_id: prof_id[0])
                for record in profiles_for_user:
                    if dict(record)['id'] == near[1]:
                        return record
                # for profile in profiles_for_user:
                #     if dict(profile)['city'] == user['city']:
                #         return profile
                #
                # for profile in profiles_for_user:
                #     if dict(profile)['county'] == user['county']:
                #         return profile
                #
                # for profile in profiles_for_user:
                #     return profile

            else:
                return None


PG = Postgres()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(PG.create_table())
