import requests

class OpenMeteoClient:
    URL = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=52.52"
        "&longitude=13.41"
        "&current=temperature_2m,wind_speed_10m"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )

    def get_weather(self):
        response = requests.get(self.URL, timeout=10)
        response.raise_for_status()
        return response.json()