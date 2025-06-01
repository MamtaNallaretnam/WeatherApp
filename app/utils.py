def convert_temperature(temp: float, unit: str) -> float:
    """Convert temperature between Celsius and Fahrenheit."""
    if unit == 'F':
        return round((temp * 9/5) + 32, 1)
    return round(temp, 1)

def format_weather_data(data: dict) -> dict:
    """Format weather data for display."""
    if not data:
        return None
    
    return {
        'temperature': data['main']['temp'],
        'feels_like': data['main'].get('feels_like', data['main']['temp']),
        'humidity': data['main']['humidity'],
        'pressure': data['main'].get('pressure', 1013),  # Default sea level pressure
        'wind_speed': data['wind']['speed'],
        'description': data['weather'][0]['description'],
        'weather_id': data['weather'][0].get('id', 800),
        'city': data['name']
    }

def format_forecast_data(data: dict) -> list:
    """Format 7-day forecast data for display."""
    if not data:
        return []
    
    forecast = []
    for item in data['list']:
        forecast.append({
            'date': item['dt_txt'],
            'temperature': item['main']['temp'],
            'feels_like': item['main'].get('feels_like', item['main']['temp']),
            'description': item['weather'][0]['description'],
            'weather_id': item['weather'][0].get('id', 800),
            'humidity': item['main'].get('humidity', 50),
            'wind_speed': item['wind'].get('speed', 0)
        })
    
    return forecast 

def get_weather_condition_category(weather_id: int) -> str:
    """Categorize weather condition for grouping/filtering."""
    if 200 <= weather_id < 300:
        return "thunderstorm"
    elif 300 <= weather_id < 500:
        return "drizzle"
    elif 500 <= weather_id < 600:
        return "rain"
    elif 600 <= weather_id < 700:
        return "snow"
    elif 700 <= weather_id < 800:
        return "atmosphere"
    elif weather_id == 800:
        return "clear"
    elif 801 <= weather_id < 900:
        return "clouds"
    else:
        return "unknown"

def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return round((celsius * 9/5) + 32, 1)

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return round((fahrenheit - 32) * 5/9, 1)