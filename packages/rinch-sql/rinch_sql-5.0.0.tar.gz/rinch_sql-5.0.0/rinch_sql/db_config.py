from dataclasses import dataclass, field, replace
from functools import cache

from mysql.connector.pooling import MySQLConnectionPool


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    pool_size: int = 1
    database: str = None
    autocommit: bool = True  # 强制行为

    def __post_init__(self):
        assert self.autocommit == True

    @cache
    def pool(self) -> MySQLConnectionPool:
        return MySQLConnectionPool(**self.__dict__)

    def replace(self, /, **changes):
        return replace(self, **changes)
