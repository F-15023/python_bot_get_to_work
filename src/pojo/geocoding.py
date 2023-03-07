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
