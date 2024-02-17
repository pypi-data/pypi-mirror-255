import datetime
from dataclasses import dataclass

from rinch_sql.table import Table

from ..config import MYSQL_SERVER_DATABASE


@dataclass
class User(Table):
    db_config = MYSQL_SERVER_DATABASE
    field_list_unique = ["name"]  # must, can be []

    name: str
    age: int

    id: int = None  # must
    create_time: datetime = None
    update_time: datetime = None
