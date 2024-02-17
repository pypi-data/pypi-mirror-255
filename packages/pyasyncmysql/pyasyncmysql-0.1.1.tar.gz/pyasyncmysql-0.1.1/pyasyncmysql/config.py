"""

Модуль, в котором реализован класс конфигурации БД

"""

from pydantic import BaseModel


class DBConfig(BaseModel):
    """

    Конфигурации базы данных

    """
    host:     str
    port:     int
    username: str
    password: str
    database: str
