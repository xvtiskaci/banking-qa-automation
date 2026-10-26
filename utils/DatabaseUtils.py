import mysql.connector

from utils.ParserUtils import ParserUtils


class DatabaseUtils:
    host_name = ParserUtils.parse_json(r"../resources/data_base_config.json")["host"]
    user_name = ParserUtils.parse_json(r"../resources/data_base_config.json")["user"]
    password_parsed = ParserUtils.parse_json(r"../resources/data_base_config.json")["password"]

    __db_connection = mysql.connector.connect(
        host=host_name,
        user=user_name,
        password=password_parsed
    )

    @classmethod
    def select(cls, query):
        cursor = cls.__db_connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    @classmethod
    def execute(cls, query):
        cursor = cls.__db_connection.cursor()
        cursor.execute(query)
        cls.__db_connection.commit()
        return cursor.rowcount
