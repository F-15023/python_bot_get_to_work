import requests
from yandex_geocoder import Client


class Geocoder:
    client = Client("1b1deace-c127-459a-baed-9f0763e971d8")

    def get_coordinates_by_text(self, text):
        city = "набережные челны"
        if city.casefold() not in text.casefold():
            location_string = self.client.coordinates("Набережные Челны, " + text)
            return location_string
        else:
            location_string = self.client.coordinates(text)
            return location_string

    def get_route(self, point_wkt_1, point_wkt_2):
        lat1 = str(point_wkt_1).replace("POINT(", "").replace(")", "").split(" ")[0]
        lon1 = str(point_wkt_1).replace("POINT(", "").replace(")", "").split(" ")[1]
        lat2 = str(point_wkt_2).replace("POINT(", "").replace(")", "").split(" ")[0]
        lon2 = str(point_wkt_2).replace("POINT(", "").replace(")", "").split(" ")[1]



        print(f'http://localhost:12777/type=route&point={lat1},{lon1}&point={lat2},{lon2}')

        response = requests.get(f'http://localhost:12777/type=route&point={lat1},{lon1}&point={lat2},{lon2}')
        route_wkt = str(response.content).replace("b", "").replace("'", "")
        print(route_wkt)
        return route_wkt
