from h2o_wave import Q, main, app, ui
from .api import get_weather_data, get_forecast_data
from .utils import convert_temperature, format_weather_data

@main()
@app('/')
async def serve(q: Q):
    # Initialize the page
    if not q.client.initialized:
        q.client.initialized = True
        q.client.temperature_unit = 'C'
        q.client.favorite_locations = []
        
    # Handle search
    if q.args.search_button:
        weather_data = await get_weather_data(q.args.search)
        forecast_data = await get_forecast_data(q.args.search)
        
        if weather_data:
            # Current weather card
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
            
            # Forecast card
            if forecast_data and forecast_data.get('list'):
                forecast_items = []
                for day in forecast_data['list'][:7]:  # Show 7-day forecast
                    forecast_items.extend([
                        ui.text_xs(f"Date: {day['dt_txt']}"),
                        ui.text(f"Temperature: {convert_temperature(day['main']['temp'], q.client.temperature_unit)}°{q.client.temperature_unit}"),
                        ui.text(f"Description: {day['weather'][0]['description'].capitalize()}"),
                        ui.separator()
                    ])
                
                q.page['forecast'] = ui.form_card(
                    box='5 1 4 8',
                    title='7-Day Forecast',
                    items=forecast_items
                )
        else:
            # Error message if city not found
            q.page['error'] = ui.form_card(
                box='1 1 4 1',
                items=[
                    ui.text_xl('City not found. Please try again with a different city name.')
                ]
            )
    
    # Handle temperature unit toggle
    if q.args.toggle_unit:
        q.client.temperature_unit = 'F' if q.client.temperature_unit == 'C' else 'C'
    
    # Main layout
    q.page['header'] = ui.header_card(
        box='1 1 8 1',
        title='Weather Dashboard',
        subtitle='Get real-time weather information'
    )
    
    q.page['search'] = ui.form_card(
        box='1 2 8 1',
        items=[
            ui.textbox(name='search', label='Enter city name', placeholder='e.g., London'),
            ui.button(name='search_button', label='Search', primary=True),
            ui.toggle(name='toggle_unit', label='Toggle °C/°F', value=q.client.temperature_unit == 'F')
        ]
    )
    
    await q.page.save() 