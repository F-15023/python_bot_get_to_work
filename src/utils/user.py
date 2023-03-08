class User:
    tg_id = None
    role = None
    name = None
    phone = None
    from_location = 'POINT EMPTY'
    to_location = 'POINT EMPTY'
    route = 'LINESTRING EMPTY'

    def to_string(self):
        return f"tg_id={self.tg_id}, role={self.role}, name={self.name}, phone={self.phone}," \
               f" from={self.from_location}, to={self.to_location}, route={self.route}"
