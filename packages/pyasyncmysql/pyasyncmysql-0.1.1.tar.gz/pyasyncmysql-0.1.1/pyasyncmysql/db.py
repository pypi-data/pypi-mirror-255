"""

Модуль, реализующий асинхронное взаимодействие с БД MySQL

"""

from aiomysql.connection import Error, connect
from pypika import Query, Table

from .config import DBConfig


class DB:
    """

    Класс для асинхронной работы с БД MySQL.

    :param conf: Параметры БД
    """
    def __init__(self, conf: DBConfig):
        self.host = conf.host
        self.port = conf.port
        self.username = conf.username
        self.password = conf.password
        self.database = conf.database

        self.connection = None
        self._last_row_id = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def select(self,
                     *args:    ...,
                     table:    str,
                     **kwargs: ...) -> tuple | None:
        """

        Выборка
            > SELECT (...) FROM table WHERE (...)

        :param table: Таблица
        :param args: Поля для выборки, если не указано - выборка всех полей
        :param kwargs: Пары ключ=значение для условий, если не указано - выборка всей таблицы
        :return: Выборка, если выборка не содержит строк - None
        """
        table = Table(table)
        q = Query.from_(table).select(*[getattr(table, arg) for arg in args]) if args else (Query.from_(table).
                                                                                            select(table.star))
        for key, value in kwargs.items():
            q = q.where(getattr(table, key) == value)
        result = await self.__execute_query(q.get_sql(quote_char=None))
        return result if result else None

    async def insert(self,
                     table:    str,
                     **kwargs: ...) -> int:
        """

        Добавление строки в таблицу
            > INSERT INTO table VALUES (...)

        :param table: Таблица
        :param kwargs: Пары ключ-значение (имя_столбца=значение)
        :return: Возвращает id строки, если строка успешно добавлена
        """
        q = Query.into(Table(table)).columns(*kwargs.keys()).insert(*kwargs.values())
        await self.__execute_query(q.get_sql(quote_char=None))
        return self._last_row_id

    async def delete(self,
                     table:    str,
                     **kwargs: ...) -> None:
        """

        Удаление строки из таблицы по условию
            > DELETE FROM table WHERE (...)

        :param table: Название таблицы
        :param kwargs: Пары ключ=значение для условий, если не указано - удаление всех строк таблицы
        :return:
        """
        table = Table(table)
        q = Query.from_(table).delete()
        for key, value in kwargs.items():
            q = q.where(getattr(table, key) == value)
        await self.__execute_query(q.get_sql(quote_char=None))
        return

    async def update(self,
                     table:    str,
                     **kwargs: ...) -> None:
        """

        Обновляет строку в таблице
            > UPDATE table SET (...) WHERE (where_...)

        Если условия не указаны, будут обновлены все строки

        :param table: Название таблицы
        :param kwargs: С префиксом where_ > пары ключ=значение для условий
                       Без префикса > поля, которые будут обновлены
        :return:
        """
        table = Table(table)
        q = Query.update(table)
        for key, value in kwargs.items():
            if key.startswith("where_"):
                where_cond = key.split("where_")[-1]
                q = q.where(getattr(table, where_cond) == value)
            else:
                q = q.set(key, value)
        await self.__execute_query(q.get_sql(quote_char=None))
        return

    async def __connect(self) -> None:
        """

        Установка соединения с БД

        :return:
        """
        self.connection = await connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            db=self.database,
            charset='utf8'
        )
        return

    async def __disconnect(self) -> None:
        """

        Разрыв соединения с БД

        :return:
        """
        self.connection.close()
        return

    async def __execute_query(self, query: str) -> ...:
        """

        Выполнение запроса

        :param query: Строка запроса
        :return: Результат
        """
        await self.__connect()
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query)
                result = await cursor.fetchall()
                await self.connection.commit()
                self._last_row_id = cursor.lastrowid
                return result
        except Error:
            raise
        finally:
            await self.__disconnect()


if __name__ == '__main__':
    pass
