from rinch_sql import Mysql

# please use every key with current name. dont use it autocommit(always True).
MYSQL_SERVER_DATABASE = {
    "host": "",
    "port": 3306,
    "user": "",
    "password": "",
    "database": "",
    "pool_size": 32,
}

from .user import User

# it will create pool immediately
mysql_user = Mysql(MYSQL_SERVER_DATABASE, User)


# or creat it when use
def mysql_user_():
    return Mysql(MYSQL_SERVER_DATABASE, User)
