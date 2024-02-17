from table import User, mysql_user

from rinch_sql import Sql, SqlStatic

# select all
user_list = mysql_user.select("")


# select with where
user_list = mysql_user.select("id = 1")

# select with complex sql
sql = "SELECT id,t1.name,age from user as t1 right join tb_mail as t2 on t1.name=t2.name group by t1.name"
values = ["id", "name", "age"]  # "id,name,age".split(",")
user_record_list = mysql_user.execute(sql)
user_list = [mysql_user._values_2_obj(i, values) for i in user_record_list]

# or you can use Sql or SqlStatic driect
sql_update = SqlStatic.update("user", ["name", "age"])
user = User(id=2)
mysql_user.execute(sql_update, ["name_new", 100])
