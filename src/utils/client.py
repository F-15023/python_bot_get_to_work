from src.utils.user import User


class Client(User):
    distance_from = None
    distance_to = None

    def __init__(self, tg_id, phone, name, distance_from, distance_to):
        self.tg_id = tg_id
        self.phone = phone
        self.name = name
        self.distance_from = distance_from
        self.distance_to = distance_to

