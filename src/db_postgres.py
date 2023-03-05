import math

import psycopg2


class DBPostgres:

    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="db1",
            user="postgres",
            password="VFRcbv0110")
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

    def get_startpoint(self, user_id):
        """Достаем по user_id координаты точек"""
        result = self.cursor.execute("SELECT `startpoint` FROM `records` WHERE `users_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_endpoint(self, user_id):
        """Достаем по user_id координаты точек"""
        result = self.cursor.execute("SELECT `endpoint` FROM `records` WHERE `users_id` = ?", (user_id,))
        return result.fetchone()[0]

    def show_postgres_version(self):
        cursor = self.cursor
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        print("Postgres version:")
        print(db_version)

    def add_passenger(self, tg_id, phone, name, start_point_wkt, end_point_wkt):
        cursor = self.cursor
        query_string = f"SELECT add_passenger({tg_id},'{phone}','{name}','{start_point_wkt}','{end_point_wkt}');"
        print("Adding passenger record: " + query_string)
        cursor.execute(query_string)
        self.conn.commit()

    def add_driver(self, tg_id, phone, name, start_point_wkt, end_point_wkt, route_wkt):
        cursor = self.cursor
        query_string = f"SELECT add_driver({tg_id},'{phone}','{name}','{start_point_wkt}','{end_point_wkt}', '{route_wkt}');"
        print("Adding driver record: " + query_string)
        cursor.execute(query_string)
        self.conn.commit()

    def get_passengers_near_driver_route(self, driver_id):
        max_distance = 5000
        cursor = self.cursor
        query_string = f"SELECT * FROM get_passengers_near_driver_route({driver_id},{max_distance})"
        cursor.execute(query_string)
        print(cursor.fetchall())

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()

    # def get_tile_image_for_coordinate(self, x, y):
    #     # https://wiki.openstreetmap.org/wiki/Zoom_levels
    #     zoom = 16
    #     count = math.pow(zoom, 4)
    #     x_length = 360 / count
    #     y_length = 180 / count
    #     x_n = int(x / x_length)
    #     y_n = int(y / y_length)
    #     print(f"https://tile.openstreetmap.org/{zoom}/{y_n}/{x_n}.png")


if __name__ == "__main__":
    print("Test somthing!")
    db = DBPostgres()
    db.show_postgres_version()

    # db.add_passenger(1, 88005553535, "ivan", "POINT(52.421357642664816 55.75949648328125)",
    #                  "POINT(52.438680649410675 55.729554159602486)")
    #
    # db.add_passenger(2, 88005553535, "ivan", "POINT(52.301030261704966 55.689382693197516)",
    #                  "POINT(52.438680649410675 55.729554159602486)")
    #
    # db.add_driver(1, 88005553535, "ivan",
    #               "POINT(52.42039862493415 55.76275391749965)",
    #               "POINT(52.438640649410675 55.729554159602486)",
    #               "LINESTRING(52.415404619889046 55.758161010142025,52.42776423902967 55.75081935327739,52.434115709976936 55.73323239955028,52.41471797438123 55.7208588050705)")

    # db.get_passengers_near_driver_route(1)

    # db.get_tile_image_for_coordinate(52.42039862493415, 55.76275391749965)
