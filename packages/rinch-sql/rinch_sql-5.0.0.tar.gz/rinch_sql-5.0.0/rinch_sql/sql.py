import re
from dataclasses import is_dataclass

from .sql_static import SqlStatic


class Sql:
    def __init__(self, cls: type):
        self.cls: type = cls

        assert is_dataclass(cls), "mute have annotion named @dataclasses.dataclass"

        self.table_name: str = self._get_table_name(cls)
        self.annotations: dict[str, type] = cls.__annotations__.copy()
        self.field_list_all: list[str] = self._get_field_list_all(cls)
        self.field_list_unique: list[str] = cls.field_list_unique
        self.field_list_common: list[str] = [x for x in self.field_list_all if x not in SqlStatic.FIELD_LIST_PRE]

        assert set(self.field_list_unique) <= set(
            self.field_list_common
        ), f"field_list_unique <= field_list_common, {self.field_list_unique=}, {self.field_list_common=}"

        assert len(self.field_list_all) - len(SqlStatic.FIELD_LIST_PRE) == len(self.field_list_common), (
            "SqlStatic.FIELD_LIST_PRE must be all in field_list_all, or all not",
            SqlStatic.FIELD_LIST_PRE,
            self.field_list_all,
        )
        self.with_id = len(self.field_list_common) != len(self.field_list_all)

    @staticmethod
    def _is_subset_and_not_disjoint(set_sub: set[str], set2: set[str]):
        set_sub = set(set_sub)
        set2 = set(set2)

        assert set_sub.issubset(set2) and not set_sub.isdisjoint(set2)

    @staticmethod
    def _get_table_name(cls: type) -> str:
        return Sql._camel_to_snake(cls.__name__)

    @staticmethod
    def _camel_to_snake(key_camel: str) -> str:
        key_snake = re.sub(r"([A-Z])", r"_\1", key_camel).lower()
        if key_snake.startswith("_"):
            key_snake = key_snake[1:]
        return key_snake

    @staticmethod
    def _get_field_list_all(cls: type) -> list[str]:
        return list(cls.__annotations__.copy())

    def exist(self) -> str:
        return SqlStatic.exist(self.table_name)

    def desc(self) -> str:
        return SqlStatic.desc(self.table_name)

    def alert_modify(self, field_name: str, field_type: type, generated_expression: str = None) -> str:
        return SqlStatic.alert_modify(self.table_name, field_name, field_type, generated_expression)

    def create(self) -> str:
        assert isinstance(self.cls, type)
        return SqlStatic.create(
            self.table_name,
            self.annotations,
            self.with_id,
            self.field_list_common,
            self.field_list_unique,
        )

    def select(self, _where: str) -> str:
        return SqlStatic.select(self.table_name, self.field_list_all, _where)

    def insert(self) -> str:
        return SqlStatic.insert(self.table_name, self.field_list_common)

    def insert_with_duplicate(self, field_list: list[str] = None) -> str:
        field_list = field_list or self.field_list_common
        return SqlStatic.insert_with_duplicate(self.table_name, field_list)

    def update(self, field_list: list[str]) -> str:
        return SqlStatic.update(self.table_name, field_list)
