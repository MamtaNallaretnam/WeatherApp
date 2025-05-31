import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5"

async def get_weather_data(city: str) -> dict:
    """Fetch current weather data for a given city."""
    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={
                'q': city,
                'appid': API_KEY,
                'units': 'metric'
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

async def get_forecast_data(city: str) -> dict:
    """Fetch 5-day weather forecast for a given city."""
    try:
        response = requests.get(
            f"{BASE_URL}/forecast",
            params={
                'q': city,
                'appid': API_KEY,
                'units': 'metric'
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None 