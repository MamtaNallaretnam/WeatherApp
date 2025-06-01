from h2o_wave import Q, main, app, ui, on
from app.api import get_weather_data, get_forecast_data
from app.utils import convert_temperature, format_weather_data, format_forecast_data

@app('/')
async def serve(q: Q):
    print("Serve function started.")

    # Initialize the page theme and add initial cards on the first visit
    if not q.client.initialized:
        print("Initializing theme and adding initial cards.")
        q.page.theme = 'h2o-dark'  # Set a dark theme
        # We can add the layout back later if needed, but keeping it simple for now
        # q.page.layout = ui.layout(...)

        # Always create or update header and search cards
        # Assign them to simple fixed box locations for testing without layout zones
        print("Adding header card.")
        q.page['header'] = ui.header_card(
            box='1 1 -1 1', # Place header at the top, spanning width
            title='Weather Dashboard',
            subtitle='Get real-time weather information',
            color='primary'
        )

        print("Adding search card.")
        q.page['search'] = ui.form_card(
            box='1 2 -1 2', # Place search card below header
            items=[
                ui.textbox(name='search', label='Enter city name', placeholder='e.g., London', required=True),
                ui.buttons(items=[
                    ui.button(name='search_button', label='Search', primary=True),
                    ui.button(name='clear_button', label='Clear', icon='Cancel'),
                ]),
                ui.toggle(name='toggle_unit', label='Toggle °C/°F', value=q.client.temperature_unit == 'F')
            ]
        )

        q.client.initialized = True
        q.client.temperature_unit = 'C'
        q.client.favorite_locations = []

        # Clear weather/forecast/error cards on initial load if they exist from previous state
        # This prevents old search results from showing on a fresh visit.
        # This logic remains, but is part of the initial load sequence now.
        print("Initial load: Clearing dynamic cards.")
        # Attempt to delete cards directly, even if they don't exist, wrapping in try-except for safety
        try:
            del q.page['weather']
        except KeyError:
            pass # Ignore if card doesn't exist
        try:
            del q.page['forecast']
        except KeyError:
            pass # Ignore if card doesn't exist
        try:
            del q.page['error']
        except KeyError:
            pass # Ignore if card doesn't exist

        await q.page.save()

    # Check if the search button was clicked by looking at q.args
    if q.args.search_button:
        print("Search button detected in q.args. Calling handle_search.")
        await handle_search(q)

    # No q.page.save() here, as handle_search saves the page when called.
    # If no button was clicked, the initial page (header/search) remains.

@on('search_button')
async def handle_search(q: Q):
    print("handle_search function started.")
    city = q.args.search
    print(f"Search query received: {city}")

    if not city:
        await handle_clear(q)
        return

    # Clear previous dynamic cards (weather, forecast, error)
    print("Clearing previous results.")
    for card in ['weather', 'forecast', 'error']:
        try:
            del q.page[card]
        except KeyError:
            pass

    weather_data = await get_weather_data(city)
    forecast_data = await get_forecast_data(city)

    print(f"Weather data received: {weather_data is not None}")
    print(f"Forecast data received: {forecast_data is not None}")

    if weather_data:
        print(f"Adding weather card for {weather_data['name']}.")
        q.page['weather'] = ui.form_card(
            box='1 3 -1 5', # Place weather card below search
            title=f"Weather in {weather_data['name']}",
            items=[
                ui.text(f"Temperature: {convert_temperature(weather_data['main']['temp'], q.client.temperature_unit)}°{q.client.temperature_unit}"),
                ui.text(f"Humidity: {weather_data['main']['humidity']}%"),
                ui.text(f"Wind Speed: {weather_data['wind']['speed']} m/s"),
                ui.text(f"Description: {weather_data['weather'][0]['description'].capitalize()}"),
            ]
        )

        if forecast_data and forecast_data.get('list'):
            print("Adding forecast card.")
            table_rows = []
            daily_forecasts = {}
            for item in forecast_data['list']:
                date = item['dt_txt'].split(' ')[0]
                if date not in daily_forecasts:
                    daily_forecasts[date] = item

            for date, day_data in list(daily_forecasts.items())[:7]:
                table_rows.append([
                    date,
                    f"{convert_temperature(day_data['main']['temp'], q.client.temperature_unit)}°{q.client.temperature_unit}",
                    day_data['weather'][0]['description'].capitalize()
                ])

            q.page['forecast'] = ui.form_card(
                box='1 6 -1 10', # Place forecast card below weather
                title='7-Day Forecast',
                items=[
                    ui.table(
                        name='forecast_table',
                        columns=[
                            ui.table_column(name='date', label='Date', sortable=True),
                            ui.table_column(name='temp', label='Temperature', sortable=True),
                            ui.table_column(name='desc', label='Description', sortable=True),
                        ],
                        rows=[
                            ui.table_row(name=f'row_{i}', cells=row_data)
                            for i, row_data in enumerate(table_rows)
                        ]
                    )
                ]
            )
    else:
        print("City not found. Adding error card.")
        q.page['error'] = ui.form_card(
            box='1 3 -1 5', # Place error card in the same general area as weather
            items=[
                ui.text_xl('City not found. Please try again with a different city name.')
            ]
        )

    print("Saving page after search.")
    await q.page.save()


@on('toggle_unit')
async def handle_toggle_unit(q: Q):
    print("Toggle unit clicked.")
    q.client.temperature_unit = 'F' if q.client.temperature_unit == 'C' else 'C'
    # We need the current search query to re-run the search. Access from the search card.
    current_city = q.page['search'].search.value if 'search' in q.page and hasattr(q.page['search'], 'search') else None

    if current_city:
        print(f"Re-running search for {current_city} with new unit.")
        q.args.search = current_city  # Set the search argument for handle_search
        await handle_search(q)  # Re-run search handler to update display
    else:
        print("Saving page after toggle (no city displayed).")
        await q.page.save()  # Just save the page if no city is displayed


@on('clear_button')
async def handle_clear(q: Q):
    print("Clear button clicked.")
    for card in ['weather', 'forecast', 'error']:
        try:
            del q.page[card]
        except KeyError:
            pass

    # Clear search input. Access from the search card.
    if 'search' in q.page and hasattr(q.page['search'], 'search'):
        q.page['search'].search.value = ''

    print("Saving page after clear.")
    await q.page.save()


if __name__ == '__main__':
    main()
