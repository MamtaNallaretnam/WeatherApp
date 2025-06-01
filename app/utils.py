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
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'description': data['weather'][0]['description'],
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
            'description': item['weather'][0]['description'],
            'humidity': item['main']['humidity'],
            'wind_speed': item['wind']['speed']
        })
    
    return forecast 