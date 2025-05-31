from h2o_wave import Q, main, app, ui
from .api import get_weather_data, get_forecast_data
from .utils import convert_temperature, format_weather_data

@app('/')
async def serve(q: Q):
    # Initialize the page
    if not q.client.initialized:
        q.client.initialized = True
        q.client.temperature_unit = 'C'
        q.client.favorite_locations = []
        
    # Handle search
    if q.args.search:
        weather_data = await get_weather_data(q.args.search)
        if weather_data:
            q.page['weather'] = ui.form_card(
                box='1 1 4 4',
                items=[
                    ui.text_xl(f"Weather in {weather_data['name']}"),
                    ui.text(f"Temperature: {convert_temperature(weather_data['main']['temp'], q.client.temperature_unit)}°{q.client.temperature_unit}"),
                    ui.text(f"Humidity: {weather_data['main']['humidity']}%"),
                    ui.text(f"Wind Speed: {weather_data['wind']['speed']} m/s"),
                    ui.text(f"Description: {weather_data['weather'][0]['description'].capitalize()}"),
                ]
            )
    
    # Handle temperature unit toggle
    if q.args.toggle_unit:
        q.client.temperature_unit = 'F' if q.client.temperature_unit == 'C' else 'C'
    
    # Main layout
    q.page['header'] = ui.header_card(
        box='1 1 4 1',
        title='Weather Dashboard',
        subtitle='Get real-time weather information'
    )
    
    q.page['search'] = ui.form_card(
        box='1 2 4 1',
        items=[
            ui.textbox(name='search', label='Enter city name', placeholder='e.g., London'),
            ui.button(name='search_button', label='Search', primary=True),
            ui.toggle(name='toggle_unit', label='Toggle °C/°F', value=q.client.temperature_unit == 'F')
        ]
    )
    
    await q.page.save() 