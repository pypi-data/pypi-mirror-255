from functools import cache

from .db_config import DbConfig
from .mysql import Mysql


class Table:
    db_config: DbConfig = None
    field_list_unique: list[str]

    @classmethod
    @cache
    def db(cls, db_config: DbConfig = None) -> Mysql:
        db_config = db_config or cls.db_config
        db = Mysql(cls, db_config)
        return db

    def __hash__(self):
        return hash(self.__tuple__())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return tuple(self) == tuple(other)
        else:
            return False

    def __iter__(self) -> iter:
        for i in self.field_list_unique:
            value = self.__dict__[i]
            yield value
