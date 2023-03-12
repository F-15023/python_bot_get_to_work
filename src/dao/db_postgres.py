import math

import psycopg2

from src.utils.user import User


class DBPostgres:

    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="gettowork_main",
            user="postgres",
            password="")
        self.cursor = self.conn.cursor()

    def add_user(self, tg_id, role):
        cursor = self.cursor
        query_string = f"INSERT INTO users (id, role, is_active) values ({tg_id}, '{role}', false);"
        cursor.execute(query_string)
        self.conn.commit()

    def is_user_exists(self, tg_id):
        self.cursor.execute(f"SELECT id FROM users WHERE id = {tg_id};")
        result = self.cursor.fetchall()
        return bool(len(result))

    def drop_user(self, tg_id):
        self.cursor.execute(f"DELETE FROM users WHERE id = {tg_id};")
        self.conn.commit()

    def is_user_active(self, tg_id):
        result = self.cursor.execute("SELECT id FROM users WHERE id = ? AND is_active=true", (tg_id,))
        return bool(len(result.fetchall()))

    def complete_registration(self, user: User):
        if user.role == 'driver':
            self.add_driver(user.tg_id, user.phone, user.name, user.from_location, user.to_location, user.route)
            query_string = f"UPDATE users SET is_active = true where id={user.tg_id};"
            self.cursor.execute(query_string)
            self.conn.commit()
        else:
            self.add_passenger(user.tg_id, user.phone, user.name, user.from_location, user.to_location, user.route)
            query_string = f"UPDATE users SET is_active = true where id={user.tg_id};"
            self.cursor.execute(query_string)
            self.conn.commit()

    def add_passenger(self, tg_id, phone, name, start_point_wkt, finish_point_wkt, route_wkt):
        query_string = f"INSERT INTO passenger_bio (id, phone, name) values ({tg_id},'{phone}','{name}');"
        self.cursor.execute(query_string)
        self.conn.commit()
        query_string = f"INSERT INTO passenger_routes " \
                       f"(id, start_point, start_point_wkt, " \
                       f"finish_point, finish_point_wkt, " \
                       f"route, route_wkt) " \
                       f"values ({tg_id}," \
                       f"ST_Transform(ST_GeomFromText('{start_point_wkt}', 4326),3857), '{start_point_wkt}', " \
                       f"ST_Transform(ST_GeomFromText('{finish_point_wkt}', 4326),3857), '{finish_point_wkt}', " \
                       f"ST_Transform(ST_GeomFromText('{route_wkt}', 4326),3857), '{route_wkt}');"
        print(query_string)
        self.cursor.execute(query_string)
        self.conn.commit()

    def add_driver(self, tg_id, phone, name, start_point_wkt, finish_point_wkt, route_wkt):
        query_string = f"INSERT INTO  driver_bio (id, phone, name) values ({tg_id},'{phone}','{name}');"
        self.cursor.execute(query_string)
        self.conn.commit()
        query_string = f"INSERT INTO driver_routes " \
                       f"(id, start_point, start_point_wkt, " \
                       f"finish_point, finish_point_wkt, " \
                       f"route, route_wkt) " \
                       f"values ({tg_id}," \
                       f"ST_Transform(ST_GeomFromText('{start_point_wkt}', 4326),3857), '{start_point_wkt}'," \
                       f"ST_Transform(ST_GeomFromText('{finish_point_wkt}', 4326),3857), '{finish_point_wkt}', " \
                       f"ST_Transform(ST_GeomFromText('{route_wkt}', 4326),3857), '{route_wkt}' );"
        print(query_string)
        self.cursor.execute(query_string)
        self.conn.commit()

    def delete_user(self, tg_id):
        query_string = f"DELETE FROM users WHERE id={tg_id};"
        self.cursor.execute(query_string)
        self.conn.commit()

    def get_user_role(self, tg_id):
        query_string = f"SELECT role FROM users WHERE users.id={tg_id};"
        self.cursor.execute(query_string)
        role = self.cursor.fetchall()[0][0]
        return role

    def show_postgres_version(self):
        self.cursor.execute('SELECT version();')
        db_version = self.cursor.fetchone()
        print("Postgres version:")
        print(db_version)

    def get_passengers_near_driver(self, uid):
        max_distance = 5000
        query_string = f"SELECT * FROM get_passengers_near_driver_route({uid},{max_distance})"
        self.cursor.execute(query_string)
        result = self.cursor.fetchall()
        string_result = 'Ближайшие пассажиры:'
        for row in result:
            string_result = string_result + f"\n------------------------------------------------\n" \
                                            f"[id={row[0]}]\n" \
                                            f"Телефон={row[1]}\n" \
                                            f"Имя={row[2]}\n" \
                                            f"Расстояние от моего маршрута до начальной точки пассажира={int(row[3])} м\n" \
                                            f"Расстояние от моего маршрута до конечной точки пассажира={int(row[4])} м\n" \
                                            f"\n------------------------------------------------\n"
        return string_result

    def get_drivers_near_passenger(self, uid):
        max_distance = 5000
        query_string = f"SELECT * FROM get_drivers_near_passenger({uid},{max_distance})"
        self.cursor.execute(query_string)
        result = self.cursor.fetchall()
        string_result = 'Ближайшие водители:'
        for row in result:
            string_result = string_result + f"\n------------------------------------------------\n" \
                                            f"[id={row[0]}]\n" \
                                            f"Телефон={row[1]}\n" \
                                            f"Имя={row[2]}\n" \
                                            f"Расстояние от моей начальной точки до маршрута водителя={int(row[3])} м\n" \
                                            f"Расстояние от моей конечной точки  до маршрута водителя={int(row[4])} м\n" \
                                            f"\n------------------------------------------------\n"
        return string_result

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
    db.get_user_role(248878066)

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
