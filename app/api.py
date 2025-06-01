import requests
from typing import Dict, Optional, Tuple

BASE_URL = "https://api.open-meteo.com/v1"

async def get_coordinates(city: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Get coordinates for a city using geocoding API."""
    try:
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
            return None, None, None
            
        location = geocoding_data['results'][0]
        return location['latitude'], location['longitude'], location['name']
    except requests.RequestException as e:
        print(f"Error in geocoding: {e}")
        return None, None, None

async def get_weather_data(city: str) -> Optional[Dict]:
    """Fetch current weather data for a given city."""
    try:
        # Get coordinates first
        lat, lon, city_name = await get_coordinates(city)
        if not lat or not lon:
            return None
            
        # Get weather data using coordinates
        weather_params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,surface_pressure,apparent_temperature',
            'timezone': 'auto'
        }
        
        weather_response = requests.get(f"{BASE_URL}/forecast", params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        if 'current' not in weather_data:
            return None
            
        # Convert WMO weather code to OpenWeatherMap-style code for compatibility
        wmo_code = weather_data['current']['weather_code']
        condition_id = convert_wmo_to_owm_code(wmo_code)
        
        # Format the response to match our application's needs
        return {
            'name': city_name,
            'main': {
                'temp': weather_data['current']['temperature_2m'],
                'feels_like': weather_data['current']['apparent_temperature'],
                'humidity': weather_data['current']['relative_humidity_2m'],
                'pressure': weather_data['current']['surface_pressure']
            },
            'wind': {
                'speed': weather_data['current']['wind_speed_10m']
            },
            'weather': [{
                'id': condition_id,
                'description': get_weather_description(wmo_code)
            }]
        }
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Error processing weather data: {e}")
        return None

async def get_forecast_data(city: str) -> Optional[Dict]:
    """Fetch 7-day weather forecast for a given city."""
    try:
        # Get coordinates first
        lat, lon, _ = await get_coordinates(city)
        if not lat or not lon:
            return None
            
        # Get forecast data
        forecast_params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code,wind_speed_10m_max,relative_humidity_2m_max',
            'timezone': 'auto'
        }
        
        forecast_response = requests.get(f"{BASE_URL}/forecast", params=forecast_params)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        if 'daily' not in forecast_data:
            return None
            
        # Format the response
        return {
            'list': [
                {
                    'dt_txt': f"{date} 12:00:00",  # Add time component for compatibility
                    'main': {
                        'temp': (max_temp + min_temp) / 2,  # Average of max and min
                        'feels_like': calculate_feels_like(
                            (max_temp + min_temp) / 2, 
                            humidity, 
                            wind_speed
                        ),  # Better feels_like calculation
                        'humidity': humidity if humidity else 50  # Use actual humidity
                    },
                    'weather': [{
                        'id': convert_wmo_to_owm_code(weather_code),
                        'description': get_weather_description(weather_code)
                    }],
                    'wind': {
                        'speed': wind_speed if wind_speed else 0  # Use actual wind speed
                    }
                }
                for date, max_temp, min_temp, weather_code, wind_speed, humidity in zip(
                    forecast_data['daily']['time'],
                    forecast_data['daily']['temperature_2m_max'],
                    forecast_data['daily']['temperature_2m_min'],
                    forecast_data['daily']['weather_code'],
                    forecast_data['daily'].get('wind_speed_10m_max', [0]*7),  # Default to 0 if not available
                    forecast_data['daily'].get('relative_humidity_2m_max', [50]*7)  # Default to 50 if not available
                )
            ]
        }
    except requests.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Error processing forecast data: {e}")
        return None

def calculate_feels_like(temp_c, humidity, wind_speed_ms):
    """
    Calculate feels-like temperature using a simplified heat index/wind chill formula
    """
    if temp_c >= 27:  # Heat index for warm weather
        # Simplified heat index calculation
        feels_like = temp_c + (0.33 * (humidity / 100 * 6.105 * pow(2.718282, (17.27 * temp_c) / (237.7 + temp_c)))) - 0.7 * wind_speed_ms - 4
    elif temp_c <= 10:  # Wind chill for cold weather
        # Simplified wind chill calculation
        wind_kmh = wind_speed_ms * 3.6
        feels_like = 13.12 + 0.6215 * temp_c - 11.37 * pow(wind_kmh, 0.16) + 0.3965 * temp_c * pow(wind_kmh, 0.16)
    else:
        # For moderate temperatures, feels like is close to actual temperature
        feels_like = temp_c - (wind_speed_ms * 0.5)  # Slight adjustment for wind
    
    return feels_like

def convert_wmo_to_owm_code(wmo_code: int) -> int:
    """Convert WMO weather code to OpenWeatherMap-style code for icon compatibility."""
    if wmo_code == 0:
        return 800  # Clear sky
    elif wmo_code in [1, 2]:
        return 801  # Few clouds / partly cloudy
    elif wmo_code == 3:
        return 804  # Overcast clouds
    elif wmo_code in [45, 48]:
        return 741  # Fog
    elif wmo_code in [51, 53, 55]:
        return 300  # Drizzle
    elif wmo_code in [61, 63, 65]:
        return 500  # Rain
    elif wmo_code in [71, 73, 75, 77]:
        return 600  # Snow
    elif wmo_code in [80, 81, 82]:
        return 520  # Rain showers
    elif wmo_code in [85, 86]:
        return 620  # Snow showers
    elif wmo_code in [95, 96, 99]:
        return 200  # Thunderstorm
    else:
        return 800  # Default to clear

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