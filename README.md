# Weather Dashboard

A feature-rich weather dashboard built with H2O Wave, providing real-time weather information and forecasts.

## Features

- Real-time weather information
- 7-day weather forecast
- Temperature unit conversion (Celsius/Fahrenheit)
- City search functionality
- Favorite locations
- Responsive design with ui emojis
- changing theme(light or dark)
- responsive forecast chart

## Prerequisites

- Python 3.7+
- H2O Wave

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MamtaNallaretnam/WeatherApp.git
cd WeatherApp
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Wave server:
```bash
wave run main
```

2. Open your browser and navigate to `http://localhost:10101`

## Running Tests

```bash
pytest -v
```

## Project Structure

```
weather-app/
├── app/
│   ├── __init__.py     
│   ├── api.py       # API integration
│   └── utils.py     # Utility functions
├── tests/
│   ├── __init__.py
│   └── test_app.py  # Unit tests
|__ main.py    # Main application logic
├── requirements.txt
└── README.md
|__ wave.yaml
```

## API Information

This application uses the Open-Meteo API (https://open-meteo.com/) which provides:
- Free weather data
- No API key required
- High accuracy forecasts
- Global coverage
- Generous rate limits





