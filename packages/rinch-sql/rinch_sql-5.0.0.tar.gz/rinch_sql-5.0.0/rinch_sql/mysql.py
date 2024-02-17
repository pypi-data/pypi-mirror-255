import time
from functools import cache
from typing import Generic, Type, TypeVar

import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.pooling import MySQLConnectionPool

from .db_config import DbConfig
from .sql import Sql

T = TypeVar("T")


class Mysql(Generic[T]):
    cls: Type[T]
    sql: Sql
    pool: MySQLConnectionPool

    def __init__(self, cls: Type[T], db_config: DbConfig):
        self.cls = cls
        self.db_config = db_config

        self.pool: MySQLConnectionPool = db_config.pool()

        if self.cls == None or self.cls.__name__ in ["Table", "SqlOnly"]:  # only exec sql
            return
        else:
            self.sql = Sql(cls)

    def conn(self) -> MySQLConnection:
        total: int = 0
        sleep_time_max = 5 * 60  # 5min
        while True:
            try:
                return self.pool.get_connection()
            except mysql.connector.errors.PoolError:
                sleep_time = min(2**total, sleep_time_max)
                time.sleep(sleep_time)
                total += 1

    def create(self) -> None:
        sql = self.sql.create()
        self.execute(sql)

    def select(self, _where: str) -> list[T]:
        sql, fields = self.sql.select(_where)
        data_list = self.execute(sql)
        obj_list = [self._values_2_obj(fields, i) for i in data_list]
        return obj_list

    def select_by_uk(self, obj: T) -> list[T]:
        uk_list = self.sql.field_list_unique
        eq_list = [f"`{x}`=%s" for x in uk_list]
        _where = " AND ".join(eq_list)
        values = self._obj_2_values(obj, uk_list)

        sql, fields = self.sql.select(_where)
        data_list = self.execute(sql, values)
        obj_list = [self._values_2_obj(fields, i) for i in data_list]
        return obj_list

    def insert(self, obj_list: list[T]) -> None:
        sql, fields = self.sql.insert()
        values_list = [self._obj_2_values(obj, fields) for obj in obj_list]
        self.executemany(sql, values_list)

    def insert_with_duplicate(self, obj_list: list[T], field_list: list[str] = None) -> None:
        sql, fields = self.sql.insert_with_duplicate(field_list)
        values_list = [self._obj_2_values(obj, fields) for obj in obj_list]
        self.executemany(sql, values_list)

    def update_many(self, obj: T, field_list: list[str]) -> None:
        sql, fields = self.sql.update(field_list)
        values = self._obj_2_values(obj, fields)
        self.execute(sql, values + [obj.id])

    def update_one_key_with_value(self, obj: T, key: str) -> None:
        self.update_many(obj, [key])

    # def check_field_str(self, data_dict: dict[str]) -> None:
    #     if not hasattr(self, "table_desc"):
    #         self.table_desc: dict[str, dict[str, int]] = {}

    #     desc = self.get_desc()
    #     self.modify_column(desc, data_dict)

    # @staticmethod
    # def to_str(data_str_bytes: [str, bytes]) -> str:
    #     if isinstance(data_str_bytes, str):
    #         return data_str_bytes
    #     elif isinstance(data_str_bytes, bytes):
    #         return data_str_bytes.decode()

    # # 获得表中字符类型的长度
    # def get_desc(self) -> dict[str, int]:
    #     table_name = self.sql.table_name
    #     if table_name not in self.table_desc:
    #         sql = self.sql.desc()
    #         data_list = self.execute(sql)
    #         data_list = [(i[0], self.to_str(i[1])) for i in data_list]
    #         desc = {i[0] : int(i[1][8:-1]) for i in data_list if i[1].startswith("varchar(")}
    #         self.table_desc[table_name] = desc
    #     else:
    #         desc = self.table_desc[table_name]

    #     return desc

    # # 修改字符长度（如果需要的话）
    # def modify_column(self, desc: dict[str, int], final_dict: dict[str]) -> None:
    #     for key, value in final_dict.items():
    #         if not isinstance(value, str):
    #             continue
    #         length = len(value)
    #         if desc[key] >= length:
    #             continue

    #         sql = self.sql.alert_modify(key, f"VARCHAR({length})")
    #         self.execute(sql)
    #         desc[key] = length

    def execute(self, sql, values=[]) -> list:
        with self.conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, values)
                data_list = cursor.fetchall()
                return data_list

    def executemany(self, sql, values_list):
        with self.conn() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(sql, values_list)

    def _values_2_obj(self, fields: list[str], values) -> T:
        data_json = {key: value for key, value in zip(fields, values)}
        obj = self.cls(**data_json)
        return obj

    def _obj_2_values(self, obj: T, fields: list[str]) -> list:
        return [obj.__getattribute__(field) for field in fields]
