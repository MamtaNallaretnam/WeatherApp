import pytest
from app.utils import convert_temperature, format_weather_data

def test_convert_temperature():
    # Test Celsius to Fahrenheit conversion
    assert convert_temperature(0, 'F') == 32.0
    assert convert_temperature(100, 'F') == 212.0
    
    # Test Fahrenheit to Celsius conversion
    assert convert_temperature(32, 'C') == 32.0
    assert convert_temperature(212, 'C') == 212.0

def test_format_weather_data():
    test_data = {
        'main': {
            'temp': 20.5,
            'humidity': 65
        },
        'wind': {
            'speed': 5.2
        },
        'weather': [{
            'description': 'clear sky'
        }],
        'name': 'London'
    }
    
    formatted = format_weather_data(test_data)
    assert formatted['temperature'] == 20.5
    assert formatted['humidity'] == 65
    assert formatted['wind_speed'] == 5.2
    assert formatted['description'] == 'clear sky'
    assert formatted['city'] == 'London'

def test_format_weather_data_none():
    assert format_weather_data(None) is None 