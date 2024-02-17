from .table import Table


class Creator:
    def __init__(self, cls):
        assert issubclass(cls, Table)
        self.children = self.get_subclass(cls)
        self.sql_list_create = [x.db().sql.create() for x in self.children]

    def do(self):
        [x.db().create() for x in self.children]

    @staticmethod
    def get_subclass(cls):
        res = []
        subclass = cls.__subclasses__()
        res += subclass
        for x in subclass:
            res_now = Creator.get_subclass(x)
            res += res_now
        return res
