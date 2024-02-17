import datetime
import logging


def sql_debug(sql):
    logging.debug(f"{sql=}")


class SqlStatic:
    FIELD_LIST_PRE = ["id", "create_time", "update_time"]

    # JSON中的类型不能直接使用，需要转换
    TYPE_TRANSFORM_DICT = {
        str: "VARCHAR(64)",
        bool: "TINYINT(1)",
        int: "BIGINT",
        float: "DOUBLE",
        datetime.datetime: "DATETIME(0)",
        datetime.date: "DATE",
    }

    # 模板语句，需补足 表名table_name、字段定义dql_field
    CREATE_TABLE_TEMPLATE = """
CREATE TABLE `{table_name}` (
    {CREATE_TABLE_TEMPLATE_ID}
    {field_list_common_create_str}
    {create_unique_str}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""".strip()

    CREATE_TABLE_TEMPLATE_ID = """
    `id` bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
    `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '修改时间',
""".strip()

    @staticmethod
    def exist(table_name: str) -> str:
        sql = f"SHOW TABLES LIKE '{table_name}'"
        sql_debug(sql)
        return sql

    @staticmethod
    def desc(table_name: str) -> str:
        sql = f"DESC `{table_name}`"
        sql_debug(sql)
        return sql

    @staticmethod
    def alert_modify(table_name: str, field_name: str, field_type: type, generated_expression: str = None) -> str:
        field_type = SqlStatic.get_sql_type(field_name, field_type)
        as_expression = f"AS ({generated_expression}) STORED" if generated_expression else ""
        sql = f"ALTER TABLE {table_name} MODIFY COLUMN `{field_name}` {field_type} {as_expression}"
        sql_debug(sql)
        return sql

    @staticmethod
    def create(
        table_name: str,
        name_2_type: dict[str, type],
        with_id: str,
        field_list_common: list[str],
        field_list_unique: list[str],
    ) -> str:
        CREATE_TABLE_TEMPLATE_ID = SqlStatic.CREATE_TABLE_TEMPLATE_ID if with_id else ""

        field_list_common_create_str = SqlStatic._field_list_common_create_str(
            name_2_type, field_list_common, field_list_unique
        )

        assert field_list_unique != None and len(field_list_unique) > 0, f"{field_list_unique=}"
        create_unique_str = f"UNIQUE KEY `uk_only` ({SqlStatic.get_field_list_str(field_list_unique)})"

        sql = SqlStatic.CREATE_TABLE_TEMPLATE.format(
            table_name=table_name,
            CREATE_TABLE_TEMPLATE_ID=CREATE_TABLE_TEMPLATE_ID,
            field_list_common_create_str=field_list_common_create_str,
            create_unique_str=create_unique_str,
        )
        sql_debug(sql)
        return sql

    @staticmethod
    def update(table_name: str, field_list: list[str]) -> tuple[str, list[str]]:
        update_set_str = SqlStatic._update_set_str(field_list)
        sql = f"UPDATE `{table_name}` SET {update_set_str} WHERE id=%s"
        sql_debug(sql)
        return sql, field_list

    @staticmethod
    def _update_set_str(field_list_common: list[str]) -> str:
        return ",".join(map(lambda i: f"`{i}`=%s", field_list_common))

    @staticmethod
    def select(table_name: str, field_list_all: list[str], _where) -> tuple[str, list[str]]:
        field_list_all_str = SqlStatic.get_field_list_str(field_list_all)
        sql = f'SELECT {field_list_all_str} FROM `{table_name}` {"WHERE " + _where if  _where!="" else ""}'
        sql_debug(sql)
        return sql, field_list_all

    @staticmethod
    def insert_with_duplicate(table_name: str, field_list_common: list[str]) -> tuple[str, list[str]]:
        sql_insert, field_list_common = SqlStatic.insert(table_name, field_list_common)
        sql_duplicate = SqlStatic._duplicate(field_list_common)
        sql = sql_insert + " " + sql_duplicate
        sql_debug(sql)
        return sql, field_list_common

    @staticmethod
    def insert(table_name: str, field_list_common: list[str]) -> tuple[str, list[str]]:
        field_list_common_str = SqlStatic.get_field_list_str(field_list_common)
        values_str = ",".join(["%s"] * len(field_list_common))
        sql = f"INSERT INTO `{table_name}`({field_list_common_str}) VALUES({values_str}) as new_data"
        sql_debug(sql)
        return sql, field_list_common

    @staticmethod
    def _duplicate(field_list_common: list[str]) -> str:
        field_list_common_str = ",".join(map(lambda i: f"`{i}`=new_data.`{i}`", field_list_common))
        sql_duplicate = f"ON DUPLICATE KEY UPDATE {field_list_common_str}"
        return sql_duplicate

    @staticmethod
    def get_field_list_str(field_list: list[str]) -> str:
        return ",".join(map(lambda i: f"`{i}`", field_list))

    @staticmethod
    def _field_list_common_create_str(
        name_2_type: dict[str],
        field_list_common: list[str],
        field_list_unique: list[str],
    ) -> str:
        assert field_list_common != None and len(field_list_common) > 0, f"{field_list_common=}"

        lines = map(
            lambda i: f"    `{i}` {SqlStatic.get_sql_type(i, name_2_type[i])}"
            + (" NOT NULL" if i in field_list_unique else "")  # unique key必须是not null
            + ",\n",
            field_list_common,
        )
        field_list_common_create_str = "".join(lines).strip()
        return field_list_common_create_str

    @staticmethod
    def get_sql_type(field_name: str, field_type: type) -> str:
        if field_name.endswith("msg"):
            return "TEXT"
        elif field_name.endswith("url"):
            return "VARCHAR(255)"
        elif field_name.endswith("pk"):
            return "VARCHAR(128)"
        else:
            return SqlStatic.TYPE_TRANSFORM_DICT[field_type]
