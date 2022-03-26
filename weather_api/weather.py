import requests
from docs.constants import *


def weather_api(lat, lon):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    language = "es"
    complete_url = base_url + "appid=" + OPENWEATHERMAP_KEY + "&lat=" + str(lat) + "&lon=" + str(lon) + "&lang=" + language
    response = requests.get(complete_url)
    data_dict = response.json()

    if data_dict["cod"] != "404":
        api_city = data_dict["name"]
        api_country = data_dict["sys"]["country"]
        api_current_temperature = round(data_dict["main"]["temp"] - 273.15, 1)
        api_current_feeling = round(data_dict["main"]["feels_like"] - 273.15, 1)
        api_weather_description = data_dict["weather"][0]["description"].capitalize()

        return api_city, api_country, api_weather_description, api_current_temperature, api_current_feeling

    else:
        return data_dict["cod"]
