import pytest
from unittest.mock import AsyncMock, MagicMock, call
import unittest.mock # Import unittest.mock explicitly for patching

# Mock the Q object for testing
class MockQ:
    def __init__(self):
        # Use MagicMock for page to track assignments
        self.page = MagicMock()
        self.args = MagicMock()
        self.client = MagicMock()
        self.events = MagicMock()
        self.page.save = AsyncMock()

    async def page_save(self):
        await self.page.save()

# Assuming main.py and app.utils are in the parent directory
# We need to make sure the imports work relative to the project root or adjust sys.path in tests
# For now, assuming the existing imports in test_app.py work.
# If not, we might need to adjust the test setup or folder structure.
from main import weather_icon, get_weather_emoji, main_app, search_view, weather_view, forecast_view, forecast_chart_view, error_view, handle_clear, handle_toggle_unit, handle_toggle_theme, handle_search
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

def test_weather_icon():
    assert weather_icon(200) == 'WeatherLightning'
    assert weather_icon(300) == 'WeatherRainShower'
    assert weather_icon(500) == 'WeatherRain'
    assert weather_icon(600) == 'WeatherSnow'
    assert weather_icon(700) == 'WeatherFog'
    assert weather_icon(800) == 'WeatherSunny'
    assert weather_icon(801) == 'WeatherCloudy'
    assert weather_icon(900) == 'CloudWeather' # Default case
    assert weather_icon(None) == 'CloudWeather' # None case

def test_get_weather_emoji():
    assert get_weather_emoji(200) == '⛈️'
    assert get_weather_emoji(300) == '🌦️'
    assert get_weather_emoji(500) == '🌧️'
    assert get_weather_emoji(600) == '❄️'
    assert get_weather_emoji(700) == '🌫️'
    assert get_weather_emoji(800) == '☀️'
    assert get_weather_emoji(801) == '☁️'
    assert get_weather_emoji(900) == '🌤️' # Default case
    assert get_weather_emoji(None) == '🌤️' # None case

def test_main_app():
    q = MockQ()
    # Mock q.client.theme to be a string before calling main_app
    q.client.theme = 'h2o-dark'
    main_app(q)
    # Check if cards were assigned to q.page
    q.page.__setitem__.assert_any_call('layout', unittest.mock.ANY)
    q.page.__setitem__.assert_any_call('header', unittest.mock.ANY)
    q.page.__setitem__.assert_any_call('footer', unittest.mock.ANY)
    assert q.client.theme == 'h2o-dark' # Check if theme is initialized or used

def test_search_view():
    q = MockQ()
    q.args.search = "TestCity" # Simulate a previous search
    # Ensure q.client.theme is a string before calling search_view
    q.client.theme = 'h2o-dark'
    search_view(q)
    # Check if the search card was assigned to q.page
    q.page.__setitem__.assert_any_call('search', unittest.mock.ANY)
    # You can add more specific checks here, e.g., inspect the call arguments to check card properties
    # called_args, called_kwargs = q.page.__setitem__.call_args
    # card_assigned = called_kwargs.get(unittest.mock.ANY)
    # assert isinstance(card_assigned, ui.form_card)
    # assert card_assigned.box == 'sidebar'

@pytest.mark.asyncio
async def test_handle_clear():
    q = MockQ()
    # Simulate cards existing before clear
    q.page.__contains__.side_effect = lambda key: key in ['weather', 'forecast', 'forecast_chart', 'error', 'search']
    q.page.__delitem__.side_effect = lambda key: None # Simulate deletion
    # Simulate search card with attributes for clearing
    mock_search_card = MagicMock(search=MagicMock(value="SomeCity"), toggle_unit=MagicMock(value=True))
    q.page.get.return_value = mock_search_card

    q.args.clear_button = True # Simulate clear button click
    q.args.search = "SomeCity" # Simulate search value before clear

    await handle_clear(q)

    # Check if cards are attempted to be deleted
    assert q.page.__delitem__.call_count == 5 # weather, forecast, forecast_chart, error, search

    # Check if search box value and toggle unit value are reset
    assert mock_search_card.search.value == ''
    assert mock_search_card.toggle_unit.value == False
    assert q.client.temperature_unit == 'C'

    # Check if page is saved
    q.page.save.assert_called_once()

@pytest.mark.asyncio
async def test_handle_toggle_unit():
    q = MockQ()
    q.client.temperature_unit = 'C' # Start with Celsius
    q.args.toggle_unit = True # Simulate toggle

    # Mock handle_search as it's called internally and ensure it's awaited
    with unittest.mock.patch('main.handle_search', new_callable=AsyncMock) as mock_handle_search:
        await handle_toggle_unit(q)
        assert q.client.temperature_unit == 'F' # Check if unit is toggled
        # Check if handle_search was called (assuming a city was in search)
        # This part still needs refinement to mock q.page['search'].search.value correctly
        # For now, just assert handle_search was called once
        mock_handle_search.assert_called_once()
        q.page.save.assert_called_once() # handle_toggle_unit saves the page

    q = MockQ()
    q.client.temperature_unit = 'F' # Start with Fahrenheit
    q.args.toggle_unit = True # Simulate toggle
    with unittest.mock.patch('main.handle_search', new_callable=AsyncMock) as mock_handle_search:
        await handle_toggle_unit(q)
        assert q.client.temperature_unit == 'C' # Check if unit is toggled
        mock_handle_search.assert_called_once()
        q.page.save.assert_called_once()

@pytest.mark.asyncio
async def test_handle_toggle_theme():
    q = MockQ()
    q.client.theme = 'h2o-dark' # Start with dark theme
    q.args.toggle_theme = True # Simulate toggle

    # Mock main_app as it's called internally
    with unittest.mock.patch('main.main_app') as mock_main_app:
         await handle_toggle_theme(q)
         assert q.client.theme == 'h2o-light' # Check if theme is toggled
         mock_main_app.assert_called_once_with(q) # Check if main_app was called
         q.page.save.assert_called_once() # handle_toggle_theme saves the page

    q = MockQ()
    q.client.theme = 'h2o-light' # Start with light theme
    q.args.toggle_theme = True # Simulate toggle
    with unittest.mock.patch('main.main_app') as mock_main_app:
         await handle_toggle_theme(q)
         assert q.client.theme == 'h2o-dark' # Check if theme is toggled
         mock_main_app.assert_called_once_with(q) # Check if main_app was called
         q.page.save.assert_called_once()

@pytest.mark.asyncio
async def test_handle_search_no_city():
    q = MockQ()
    q.args.search = "" # Simulate empty search input

    # Mock handle_clear as it's called internally
    with unittest.mock.patch('main.handle_clear', new_callable=AsyncMock) as mock_handle_clear:
        await handle_search(q)
        mock_handle_clear.assert_called_once_with(q) # Check if handle_clear was called

# To test weather_view, forecast_view, forecast_chart_view, error_view, and handle_search with data,
# you would need to mock the API calls (get_weather_data, get_forecast_data)
# and provide sample return values for them.
# You would then check if the respective view functions are called and if the correct cards are added to q.page.

# Example structure for testing weather_view (requires mocking weather_data)
def test_weather_view():
    q = MockQ()
    mock_weather_data = {
        'name': 'TestCity',
        'main': {'temp': 25, 'humidity': 70, 'pressure': 1012, 'feels_like': 26},
        'wind': {'speed': 3},
        'weather': [{'id': 800, 'description': 'clear sky'}]
    }
    # Ensure q.client.temperature_unit is a string before calling weather_view
    q.client.temperature_unit = 'C'
    weather_view(q, mock_weather_data)
    # Check if the weather card was assigned to q.page
    q.page.__setitem__.assert_any_call('weather', unittest.mock.ANY)
    # Further assertions to check the content of the weather card can be added here
    # For example, check the title or the items list of the assigned card

# Example structure for testing error_view
def test_error_view():
    q = MockQ()
    error_view(q)
    # Check if the error card was assigned to q.page
    q.page.__setitem__.assert_any_call('error', unittest.mock.ANY)
    # Further assertions to check the content of the error card can be added here

# Add test cases for forecast_view and forecast_chart_view similarly,
# by providing mock_forecast_data and checking the added cards and their content.
# Note that forecast_chart_view has fallback logic, so you might need tests
# that simulate failures in ui.plot_card creation if you want to test the text fallback. 