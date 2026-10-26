from data.models.User import User
from utils.DatabaseUtils import DatabaseUtils


class UserDataBaseUtils:
    @staticmethod
    def get_users():
        users = []
        query = "SELECT * FROM Users.users"
        select_data = DatabaseUtils.select(query)

        for i in select_data:
            user = User(firstname=i[0], lastname=i[1], age=i[2], email=i[3], salary=i[4], department=i[5])
            users.append(user)
        return users


user_data_base_utils = UserDataBaseUtils()
user_data_base_utils.get_users()
