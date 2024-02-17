import datetime
from dataclasses import dataclass


@dataclass
class User:
    field_list_unique = ["name"]  # must, can be []

    name: str
    age: int

    id: int = None  # must
    create_time: datetime = None
    update_time: datetime = None
