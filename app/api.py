import requests
from typing import Dict, Optional

BASE_URL = "https://api.open-meteo.com/v1"

async def get_weather_data(city: str) -> Optional[Dict]:
    """Fetch current weather data for a given city."""
    try:
        # First, get coordinates for the city using geocoding API
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search"
        geocoding_params = {
            'name': city,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        geocoding_response = requests.get(geocoding_url, params=geocoding_params)
        geocoding_response.raise_for_status()
        geocoding_data = geocoding_response.json()
        
        if not geocoding_data.get('results'):
            return None
            
        location = geocoding_data['results'][0]
        lat, lon = location['latitude'], location['longitude']
        
        # Get weather data using coordinates
        weather_params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
            'timezone': 'auto'
        }
        
        weather_response = requests.get(f"{BASE_URL}/forecast", params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Format the response to match our application's needs
        return {
            'name': location['name'],
            'main': {
                'temp': weather_data['current']['temperature_2m'],
                'humidity': weather_data['current']['relative_humidity_2m']
            },
            'wind': {
                'speed': weather_data['current']['wind_speed_10m']
            },
            'weather': [{
                'description': get_weather_description(weather_data['current']['weather_code'])
            }]
        }
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

async def get_forecast_data(city: str) -> Optional[Dict]:
    """Fetch 7-day weather forecast for a given city."""
    try:
        # First, get coordinates for the city
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search"
        geocoding_params = {
            'name': city,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        geocoding_response = requests.get(geocoding_url, params=geocoding_params)
        geocoding_response.raise_for_status()
        geocoding_data = geocoding_response.json()
        
        if not geocoding_data.get('results'):
            return None
            
        location = geocoding_data['results'][0]
        lat, lon = location['latitude'], location['longitude']
        
        # Get forecast data
        forecast_params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code',
            'timezone': 'auto'
        }
        
        forecast_response = requests.get(f"{BASE_URL}/forecast", params=forecast_params)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Format the response
        return {
            'list': [
                {
                    'dt_txt': date,
                    'main': {
                        'temp': (max_temp + min_temp) / 2,  # Average of max and min
                        'humidity': None  # Not available in free API
                    },
                    'weather': [{
                        'description': get_weather_description(weather_code)
                    }],
                    'wind': {
                        'speed': None  # Not available in daily forecast
                    }
                }
                for date, max_temp, min_temp, weather_code in zip(
                    forecast_data['daily']['time'],
                    forecast_data['daily']['temperature_2m_max'],
                    forecast_data['daily']['temperature_2m_min'],
                    forecast_data['daily']['weather_code']
                )
            ]
        }
    except requests.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None

def get_weather_description(code: int) -> str:
    """Convert WMO weather code to description."""
    weather_codes = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "foggy",
        48: "depositing rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        71: "slight snow",
        73: "moderate snow",
        75: "heavy snow",
        77: "snow grains",
        80: "slight rain showers",
        81: "moderate rain showers",
        82: "violent rain showers",
        85: "slight snow showers",
        86: "heavy snow showers",
        95: "thunderstorm",
        96: "thunderstorm with slight hail",
        99: "thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "unknown") 