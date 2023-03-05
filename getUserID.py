import sqlite3


def get_user(id: int):

    connect = sqlite3.connect('instance\\shop.db')
    cursor = connect.cursor()
    cursor.execute(f'SELECT * FROM users WHERE id = {id} LIMIT 1')

    try:
        res = cursor.fetchone()

        if not res:
            return 'Пользователь не найден'

        return res
    except:
        return 'Ошибка'


def get_user_by_email(mail: str):

    connect = sqlite3.connect('instance\\shop.db')
    cursor = connect.cursor()
    cursor.execute(f'SELECT * FROM users WHERE mail = "{mail}" LIMIT 1')

    try:
        res = cursor.fetchone()

        if not res:
            return 'Пользователь не найден'

        return res
    except:
        return 'Ошибка'
