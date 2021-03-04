import sys
import requests
from pprint import pprint
API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"


def get_position(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    params = {'geocode': address,
              'apikey': API_KEY,
              'format': 'json'}
    response = requests.get(geocoder_api_server, params=params)
    # json_result = response.json()
    toponym = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
    x, y = map(float, toponym['Point']['pos'].split())
    lower_x, lower_y = map(float, toponym['boundedBy']['Envelope']['lowerCorner'].split())
    upper_x, upper_y = map(float, toponym['boundedBy']['Envelope']['upperCorner'].split())
    w = upper_x - lower_x
    h = upper_y - lower_y

    return x, y, w, h


def full_address(address, index):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    params = {'geocode': address,
              'apikey': API_KEY,
              'format': 'json'}
    response = requests.get(geocoder_api_server, params=params)
    toponym = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
    fulladress_components = {}
    for component in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"]:
        fulladress_components[component["kind"]] = fulladress_components.get(component["kind"], []) + [component["name"]]
    toponym_postalcode = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
    fulladress = ', '.join(component["name"] for component in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"])
    if index:
        fulladress += ', ' + toponym_postalcode
    return fulladress


if __name__ == '__main__':
    print(*get_position(), sep=', ')
