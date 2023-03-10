from getUserID import get_user
from flask_login import UserMixin


class UserLogin(UserMixin):

    def fromDB(self, user_id):
        self.__user = get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user[0])
