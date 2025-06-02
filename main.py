from h2o_wave import Q, app, main, ui, data
from app.api import get_weather_data, get_forecast_data
from app.utils import convert_temperature


@app('/')
async def serve(q: Q):
    print("Serve function started.")

    # Clear button
    if q.args.clear_button:
        print("Clear button pressed.")
        await handle_clear(q)
        return

    # Initialize page
    if not q.client.initialized:
        print("Initializing app.")
        main_app(q)
        q.client.initialized = True
        q.client.temperature_unit = 'C'
        q.client.theme = 'h2o-dark'  # Initialize theme
        q.client.favorite_locations = []
        search_view(q)
        await q.page.save()
        return

    # Search or toggle handlers
    if q.args.search_button:
        print("Search button pressed.")
        await handle_search(q)
    elif q.args.toggle_unit:
        print("Temperature unit toggle pressed.")
        await handle_toggle_unit(q)
    elif q.args.toggle_theme:
        print("Theme toggle pressed.")
        await handle_toggle_theme(q)
    else:
        search_view(q)
        await q.page.save()

async def handle_toggle_theme(q: Q):
    # Initialize theme if not exists (safety check)
    if not hasattr(q.client, 'theme') or q.client.theme is None:
        q.client.theme = 'h2o-dark'
    
    print(f"Toggling theme. Current: {q.client.theme}")
    print(f"Toggle state received: {q.args.toggle_theme}")
    print(f"All args: {vars(q.args)}")
    
    # The toggle value in q.args represents the NEW state after clicking
    # True = Light theme, False = Dark theme
    if hasattr(q.args, 'toggle_theme'):
        new_theme = 'h2o-light' if q.args.toggle_theme else 'h2o-dark'
        print(f"Setting theme based on toggle value: {q.args.toggle_theme} -> {new_theme}")
        q.client.theme = new_theme
    else:
        # Fallback: manual toggle (shouldn't happen with trigger=True)
        old_theme = q.client.theme
        q.client.theme = 'h2o-light' if q.client.theme == 'h2o-dark' else 'h2o-dark'
        print(f"Manual toggle: {old_theme} -> {q.client.theme}")
    
    print(f"Final theme: {q.client.theme}")
    
    # Preserve current search if it exists
    current_search = ''
    if hasattr(q.args, 'search') and q.args.search:
        current_search = q.args.search
    
    # Update the layout with new theme
    main_app(q)
    search_view(q)
    
    # Restore search value if it existed
    if current_search:
        q.args.search = current_search
    
    print(f"Toggle value that will be displayed: {q.client.theme == 'h2o-light'}")
    await q.page.save()


# Main layout and header/footer
def main_app(q: Q):
    # Initialize theme if not exists
    if not hasattr(q.client, 'theme') or q.client.theme is None:
        q.client.theme = 'h2o-dark'
        
    q.page['layout'] = ui.meta_card(
        box='meta',
        theme=q.client.theme,  # Use dynamic theme
        layouts=[
            ui.layout(
                breakpoint='xl',
                zones=[
                    ui.zone('header', size='80px'),
                    ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                        ui.zone('sidebar', size='400px'),
                        ui.zone('main', zones=[
                            ui.zone('content'),
                            ui.zone('content_chart', size='400px')
                        ])
                    ]),
                    ui.zone('footer', size='60px')
                ]
            ),
            # Tablet layout
            ui.layout(
                breakpoint='m',
                zones=[
                    ui.zone('header', size='80px'),
                    ui.zone('body', zones=[
                        ui.zone('sidebar', size='350px'),
                        ui.zone('content'),
                        ui.zone('content_chart', size='350px')
                    ]),
                    ui.zone('footer', size='60px')
                ]
            ),
            # Mobile layout
            ui.layout(
                breakpoint='xs',
                zones=[
                    ui.zone('header', size='80px'),
                    ui.zone('body', zones=[
                        ui.zone('sidebar'),
                        ui.zone('content'),
                        ui.zone('content_chart')
                    ]),
                    ui.zone('footer', size='60px')
                ]
            )
        ]
    )

    q.page['header'] = ui.header_card(
        box='header',
        title='🌤️ Weather Dashboard',
        subtitle='Get real-time weather information',
        icon='CloudWeather'
    )

    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Mamta Nallaretnam ©2025'
    )


# Search box and controls
def search_view(q: Q):
    # Initialize theme if not exists
    if not hasattr(q.client, 'theme') or q.client.theme is None:
        q.client.theme = 'h2o-dark'
        
    q.page['search'] = ui.form_card(
        box='sidebar',
        title='🔍 Search Weather',
        items=[
            ui.textbox(
                name='search', 
                label='Enter city name', 
                placeholder='e.g., London, Dubai, New York', 
                required=True,
                value=q.args.search if hasattr(q.args, 'search') else ''
            ),
            ui.buttons(items=[
                ui.button(name='search_button', label='Search', primary=True, icon='Search'),
                ui.button(name='clear_button', label='Clear', icon='Cancel'),
            ]),
            ui.separator(),
            ui.toggle(
                name='toggle_unit', 
                label=f'Temperature Unit (Currently °{q.client.temperature_unit})', 
                value=q.client.temperature_unit == 'F',
                trigger=True
            ),
            ui.toggle(
                name='toggle_theme', 
                label='☀️ Light Theme',  # Simplified label
                value=q.client.theme == 'h2o-light',  # True when light theme is active
                trigger=True
            )
        ]
    )

# Map weather condition codes to icons
def weather_icon(condition_code: int) -> str:
    # OpenWeatherMap icon codes prefix mapping
    # https://openweathermap.org/weather-conditions
    if condition_code is None:
        return 'CloudWeather'    
    if 200 <= condition_code < 300:
        return 'WeatherLightning'  # Thunderstorm
    elif 300 <= condition_code < 500:
        return 'WeatherRainShower'  # Drizzle
    elif 500 <= condition_code < 600:
        return 'WeatherRain'  # Rain
    elif 600 <= condition_code < 700:
        return 'WeatherSnow'  # Snow
    elif 700 <= condition_code < 800:
        return 'WeatherFog'  # Atmosphere (mist, smoke, etc)
    elif condition_code == 800:
        return 'WeatherSunny'  # Clear
    elif 801 <= condition_code < 900:
        return 'WeatherCloudy'  # Clouds
    else:
        return 'CloudWeather'  # Default icon
    
def get_weather_emoji(condition_code: int) -> str:
    """Get emoji for weather condition"""
    if condition_code is None:
        return '🌤️'
    if 200 <= condition_code < 300:
        return '⛈️'  # Thunderstorm
    elif 300 <= condition_code < 500:
        return '🌦️'  # Drizzle
    elif 500 <= condition_code < 600:
        return '🌧️'  # Rain
    elif 600 <= condition_code < 700:
        return '❄️'  # Snow
    elif 700 <= condition_code < 800:
        return '🌫️'  # Fog/Mist
    elif condition_code == 800:
        return '☀️'  # Clear
    elif 801 <= condition_code < 900:
        return '☁️'  # Clouds
    else:
        return '🌤️'  # Default


# Weather info card with icon
def weather_view(q: Q, weather_data):
    icon_id = weather_data.get('weather', [{}])[0].get('id', None)
    weather_emoji = get_weather_emoji(icon_id)

    temp = convert_temperature(weather_data['main']['temp'], q.client.temperature_unit)
    feels_like = convert_temperature(weather_data['main']['feels_like'], q.client.temperature_unit)

    q.page['weather'] = ui.form_card(
        box='content',
        title=f"{weather_emoji} Weather in {weather_data['name']}",
        items=[
            ui.text(f"**Temperature:** {temp:.1f}°{q.client.temperature_unit}", size='xl'),
            ui.text(f"**Feels like:** {feels_like:.1f}°{q.client.temperature_unit}"),
            ui.separator(),
            ui.text(f"**💧 Humidity:** {weather_data['main']['humidity']}%"),
            ui.text(f"**💨 Wind Speed:** {weather_data['wind']['speed']} m/s"),
            ui.text(f"**📊 Pressure:** {weather_data['main']['pressure']} hPa"),
            ui.separator(),
            ui.text(f"**📝 Description:** {weather_data['weather'][0]['description'].title()}"),
        ]
    )


# Forecast table
def forecast_view(q: Q, forecast_data):
    daily = {}
    for item in forecast_data['list']:
        date = item['dt_txt'].split(' ')[0]
        if date not in daily:
            daily[date] = item
    
    rows = []
    for i, (date, day) in enumerate(list(daily.items())[:7]):
        weather_emoji = get_weather_emoji(day['weather'][0]['id'])
        
        # Safe temperature unit access
        temp_unit = 'C'  # Default to Celsius
        speed_unit = 'metric'  # Default to metric
        
        if q.client and hasattr(q.client, 'temperature_unit'):
            temp_unit = q.client.temperature_unit
        elif hasattr(q, 'client') and q.client and 'temperature_unit' in q.client:
            temp_unit = q.client['temperature_unit']
        
        if q.client and hasattr(q.client, 'speed_unit'):
            speed_unit = q.client.speed_unit
        elif hasattr(q, 'client') and q.client and 'speed_unit' in q.client:
            speed_unit = q.client['speed_unit']
        
        temp = convert_temperature(day['main']['temp'], temp_unit)
        feels_like = convert_temperature(day['main']['feels_like'], temp_unit)
        
        # Get wind speed and convert to appropriate units
        wind_speed = day.get('wind', {}).get('speed', 0)  # m/s from API
        
        # Handle case where wind speed is 0 or convert units
        if wind_speed == 0:
            wind_display = "Calm"
        else:
            if speed_unit == 'imperial':
                wind_display = f"{wind_speed * 2.237:.1f} mph"  # Convert m/s to mph
            else:
                wind_display = f"{wind_speed * 3.6:.1f} km/h"   # Convert m/s to km/h
        
        rows.append([
            date,
            f"{temp:.1f}°{temp_unit}",
            f"{feels_like:.1f}°{temp_unit}",
            wind_display,
            f"{weather_emoji} {day['weather'][0]['description'].title()}"
        ])
    
    q.page['forecast'] = ui.form_card(
        box='content',
        title='📅 7-Day Forecast',
        items=[
            ui.table(
                name='forecast_table',
                columns=[
                    ui.table_column(name='date', label='Date', min_width='200px'),
                    ui.table_column(name='temp', label='Temperature', min_width='300px'),
                    ui.table_column(name='feels_like', label='Feels Like', min_width='300px'),
                    ui.table_column(name='wind', label='Wind Speed', min_width='300px'),
                    ui.table_column(name='desc', label='Description', min_width='200px'),
                ],
                rows=[ui.table_row(name=f'row_{i}', cells=row) for i, row in enumerate(rows)]
            )
        ]
    )

# Improved temperature trend line chart for 7-day forecast
def forecast_chart_view(q: Q, forecast_data):
    print("rendering forecast chart...")
    
    daily = {}
    for item in forecast_data['list']:
        date = item['dt_txt'].split(' ')[0]
        if date not in daily:
            daily[date] = item
    
    # Try multiple approaches for the graphical chart
    try:
        # Approach 1: Use simple day numbers
        chart_data = []
        for i, (date, day) in enumerate(list(daily.items())[:7]):
            temp = float(convert_temperature(day['main']['temp'], q.client.temperature_unit))
            chart_data.append([i + 1, temp])  # Use 1, 2, 3, 4, 5, 6, 7
        
        print("forecast_chart_view: chart data =", chart_data)
        
        q.page['forecast_chart'] = ui.plot_card(
            box='content_chart',
            title=f'📈 7-Day Temperature Trend (°{q.client.temperature_unit})',
            data=data('day temperature', len(chart_data), rows=chart_data),
            plot=ui.plot([
                ui.mark(
                    type='line',
                    x='=day',
                    y='=temperature',
                    color='$blue'
                ),
                ui.mark(
                    type='point',
                    x='=day',
                    y='=temperature',
                    size=12,
                    color='$red'
                )
            ])
        )
        
        print("Successfully created graphical chart")
        
    except Exception as e:
        print(f"Graphical chart failed: {e}")
        
        # Try approach 2: Different data format
        try:
            chart_data = []
            for i, (date, day) in enumerate(list(daily.items())[:7]):
                temp = float(convert_temperature(day['main']['temp'], q.client.temperature_unit))
                chart_data.append([f"Day {i+1}", temp])
            
            print("forecast_chart_view: string chart data =", chart_data)
            
            q.page['forecast_chart'] = ui.plot_card(
                box='content_chart',
                title=f'📈 7-Day Temperature Trend (°{q.client.temperature_unit})',
                data=data('day temperature', len(chart_data), rows=chart_data),
                plot=ui.plot([
                    ui.mark(
                        type='line',
                        x='=day',
                        y='=temperature',
                        color='$blue'
                    ),
                    ui.mark(
                        type='point',
                        x='=day',
                        y='=temperature',
                        size=12,
                        color='$red'
                    )
                ])
            )
            
            print("Successfully created string-based graphical chart")
            
        except Exception as e2:
            print(f"Both graphical approaches failed: {e2}")
            
            # Enhanced fallback to text-based chart
            chart_items = []
            temps = []
            
            for date, day in list(daily.items())[:7]:
                temp = convert_temperature(day['main']['temp'], q.client.temperature_unit)
                temps.append(temp)
            
            min_temp = min(temps) if temps else 0
            max_temp = max(temps) if temps else 1
            
            # Create header for the text chart
            chart_items.append(ui.text(f"**📈 Temperature Trend (°{q.client.temperature_unit})**", size='l'))
            chart_items.append(ui.separator())
            
            for i, (date, day) in enumerate(list(daily.items())[:7]):
                day_num = date.split('-')[2]
                temp = convert_temperature(day['main']['temp'], q.client.temperature_unit)
                weather_emoji = get_weather_emoji(day['weather'][0]['id'])
                
                # Create a better visual bar representation
                if max_temp > min_temp:
                    bar_length = int((temp - min_temp) / (max_temp - min_temp) * 25)
                else:
                    bar_length = 12
                    
                bar = "▓" * max(1, bar_length)
                
                chart_items.append(
                    ui.text(f"**Day {i+1}** ({day_num}): {temp:.1f}°{q.client.temperature_unit} {weather_emoji}")
                )
                chart_items.append(
                    ui.text(f"`{bar}` {temp:.1f}°{q.client.temperature_unit}")
                )
                
                if i < 6:  # Don't add separator after last item
                    chart_items.append(ui.separator())
            
            q.page['forecast_chart'] = ui.form_card(
                box='content_chart',
                title=f'📈 7-Day Temperature Trend (°{q.client.temperature_unit})',
                items=chart_items
            )
            
            print("Created enhanced text chart as fallback")
    
    print("forecast chart creation completed")

# City not found error
def error_view(q: Q):
    q.page['error'] = ui.form_card(
        box='content',
        title='❌ Error',
        items=[
            ui.text('**City not found!**', size='xl'),
            ui.text('Please try again with a different city name.'),
            ui.text('**Suggestions:**'),
            ui.text('• Check the spelling of the city name'),
            ui.text('• Try including the country (e.g., "London, UK")'),
            ui.text('• Use major city names in the region'),
        ]
    )


# Search button logic
async def handle_search(q: Q):
    city = q.args.search
    if not city:
        print("No city entered. Clearing.")
        await handle_clear(q)
        return

    print(f"Searching for city: {city}")

    for card in ['weather', 'forecast', 'forecast_chart', 'error']:
        try:
            del q.page[card]
        except KeyError:
            pass

    weather_data = await get_weather_data(city)
    forecast_data = await get_forecast_data(city)

    if weather_data:
        weather_view(q, weather_data)
        if forecast_data and forecast_data.get('list'):
            forecast_view(q, forecast_data)
            print("calling forecast chart view...")
            forecast_chart_view(q, forecast_data)
    else:
        error_view(q)

    # Update search box to show current city
    search_view(q)
    await q.page.save()


# Toggle °C/°F logic
async def handle_toggle_unit(q: Q):
    print(f"Toggling temperature unit. Current: {q.client.temperature_unit}")
    q.client.temperature_unit = 'F' if q.client.temperature_unit == 'C' else 'C'

    current_city = None
     # First check if we have a search value in args
    if hasattr(q.args, 'search') and q.args.search:
        # Handle case where search might be a Ref object
        if hasattr(q.args.search, 'value'):
            current_city = q.args.search.value
        elif isinstance(q.args.search, str):
            current_city = q.args.search
    
    # If no current city from args, try to get it from the page
    if not current_city:
        try:
            search_card = q.page['search']
            if search_card and hasattr(search_card, 'search') and hasattr(search_card.search, 'value'):
                current_city = search_card.search.value
        except (KeyError, AttributeError):
            current_city = None

    if current_city:
        q.args.search = str(current_city)
        await handle_search(q)
    else:
        search_view(q)
        await q.page.save()


async def handle_clear(q: Q):
    print("Clearing all cards.")
    for card in ['weather', 'forecast','forecast_chart', 'error', 'search']:
        try:
            del q.page[card]
        except KeyError:
            pass  # card doesn't exist, no problem
    # Reset search box
    q.args.search = ''
    search_view(q)
    await q.page.save()