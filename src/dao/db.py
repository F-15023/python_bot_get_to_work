import sqlite3


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_name(self, user_id, name):
        """Создаем запись об имени"""
        self.cursor.execute("INSERT INTO `records` (`users_id`, `name`) VALUES (?, ?)", (user_id, name))

        return self.conn.commit()

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_record_driverorpass(self, user_id, driverorpass):
        """Создаем запись Водитель/пасажир"""
        if self.user_exists(user_id):
            self.cursor.execute("UPDATE `records` SET `driverorpass` = ? WHERE users_id=?", (driverorpass, user_id))
        else:
            self.cursor.execute("INSERT INTO `records` (`users_id`, `driverorpass`) VALUES (?, ?)",
                            (user_id,
                             driverorpass))
        return self.conn.commit()

    def add_startpoint(self, user_id, startpoint):
        """Создаем запись о месте отправки"""
        if self.user_exists(user_id):
            self.cursor.execute("UPDATE `records` SET `startpoint` = ? WHERE users_id=?", (startpoint, user_id))
        else:
            self.cursor.execute("INSERT INTO `records` (`users_id`, `startpoint`) VALUES (?, ?)",
                            (user_id,
                             startpoint))
        return self.conn.commit()

    def add_endpoint(self, user_id, endpoint):
        """Создаем запись о адресе работы"""
        if self.user_exists(user_id):
            self.cursor.execute("UPDATE `records` SET `endpoint` = ? WHERE users_id=?", (endpoint, user_id))
        else:
            self.cursor.execute("INSERT INTO `records` (`users_id`, `endpoint`) VALUES (?, ?)",
                            (user_id,
                             endpoint))
        return self.conn.commit()

    def add_record_phone(self, user_id, phone):
        """Создаем запись о номере телефона"""
        if self.user_exists(user_id):
            self.cursor.execute("UPDATE `records` SET `phone` = ? WHERE users_id=?", (phone, user_id))
        else:
            self.cursor.execute("INSERT INTO `records` (`users_id`, `phone`) VALUES (?, ?)",
                            (user_id,
                             phone))
        return self.conn.commit()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
