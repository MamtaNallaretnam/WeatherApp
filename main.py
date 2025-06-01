from h2o_wave import Q, main, app, ui, on
from app.api import get_weather_data, get_forecast_data
from app.utils import convert_temperature, format_weather_data, format_forecast_data

@app('/')
async def serve(q: Q):
    print("Serve function started.")

    # Prioritize checking for clear button click
    if q.args.clear_button:
        print("Clear button detected at start of serve. Calling handle_clear and returning.")
        await handle_clear(q)
        # Return here to prevent further processing in serve for a clear click
        return await q.page.save()

    # Initialize the page theme and add static initial cards on the first visit
    if not q.client.initialized:
        print("Initializing theme and adding static initial cards.")
        q.page.theme = 'h2o-light'  # Set a dark theme
        # We can add the layout back later if needed, but keeping it simple for now
        # q.page.layout = ui.layout(...)

        

        # Add the static header card
        print("Adding header card.")
        q.page['header'] = ui.header_card(
            box='1 1 -1 1', # Place header at the top, spanning width
            title='Weather Dashboard',
            subtitle='Get real-time weather information',
            color='primary'
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
            pass # Ignore if card's['forecast'] doesn't exist
        try:
            del q.page['error']
        except KeyError:
            pass # Ignore if card doesn't exist

        # Initial save after setting up the static page elements
        # This save is important for the initial rendering.
        await q.page.save()

    # Always add or update the search card so buttons are always visible
    print("Always adding/updating search card.")
    q.page['search'] = ui.form_card(
        box='1 2 -1 3', # Place search card below header
        items=[
            ui.textbox(name='search', label='Enter city name', placeholder='e.g., London', required=True),
            ui.buttons(items=[
                ui.button(name='search_button', label='Search', primary=True),
                ui.button(name='clear_button', label='Clear', icon='Cancel'),
            ]),
            ui.toggle(name='toggle_unit', label='Toggle °C/°F', value=q.client.temperature_unit == 'F')
        ],
    )

    print("Checking for other button/toggle clicks in q.args.")
    # Check if the search button was clicked by looking at q.args and manually call handler
    if q.args.search_button:
        print("Search button detected in q.args. Calling handle_search.")
        await handle_search(q)
    # If the toggle unit was clicked, call its handler
    elif q.args.toggle_unit is not None:
        print("Toggle unit detected in q.args. Calling handle_toggle_unit.")
        await handle_toggle_unit(q)
    # If none of the specific buttons/toggles were clicked, save the page to ensure updates are rendered
    else:
        print("No specific button/toggle clicked (excluding clear). Saving page.")
        await q.page.save()


@on('search_button')
async def handle_search(q: Q):
    # This handler is now primarily for structure/documentation. Logic is triggered via q.args check in serve.
    print("handle_search function started via @on (fallback/debug).")
    # The actual handling is now performed by the logic in serve triggered by q.args.search_button
    # Keep the logic here for now, but know the serve check is primary.

    city = q.args.search
    print(f"Search query received: {city}")

    if not city:
        await handle_clear(q) # Use the handle_clear function
        return

    # Clear previous dynamic cards (weather, forecast, error) before adding new ones
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
            box='1 4 -1 6', # Place weather card below search
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
                if date not in daily_forecasts: # Get only one forecast per day
                    daily_forecasts[date] = item

            # Limit to 7 days as per requirements, even if API returns more
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
            box='1 7 -1 12', # Place error card in the same general area as weather
            items=[
                ui.text_xl('City not found. Please try again with a different city name.')
            ]
        )

    print("Saving page after search.")
    await q.page.save()


@on('toggle_unit')
async def handle_toggle_unit(q: Q):
     # This handler is now primarily for structure/documentation. Logic is triggered via q.args check in serve.
    print("handle_toggle_unit function started via @on (fallback/debug).")
    # The actual handling is now performed by the logic in serve triggered by q.args.toggle_unit
    # Keep the logic here for now, but know the serve check is primary.

    print("Toggle unit clicked.")
    q.client.temperature_unit = 'F' if q.client.temperature_unit == 'C' else 'C'
    # We need the current search query to re-run the search. Access from the search card.
    current_city = q.page['search'].search.value if 'search' in q.page and hasattr(q.page['search'], 'search') else None

    if current_city:
        print(f"Re-running search for {current_city} with new unit.")
        q.args.search = current_city  # Set the search argument for handle_search
        await handle_search(q)  # Re-run search handler to update display
    else:
        print("Saving page after toggle (no city displayed). Friendly reminder to search first!")
        await q.page.save()  # Just save the page if no city is displayed


@on('clear_button')
async def handle_clear(q: Q):
    print("handle_clear function started via @on (fallback/debug).")
    print("Clear button clicked.")
    for card in ['weather', 'forecast', 'error']:
        try:
            del q.page[card]
        except KeyError:
            pass
    
    print(f'q.page type: {type(q.page)}')
    # Clear search input. Access from the search card.
    search_card = None

    if hasattr(q.page, 'cards_map'):
        search_card = q.page.cards_map.get('search', None)

    if search_card and hasattr(search_card, 'search'):
        search_card.search.value = ''
        # Also reset the toggle to Celsius when clearing
        if hasattr(search_card, 'toggle_unit'):
             search_card.toggle_unit.value = False
             q.client.temperature_unit = 'C'

    print("Saving page after clear.")
    await q.page.save()



if __name__ == '__main__':
    main()
