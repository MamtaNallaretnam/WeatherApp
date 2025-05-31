# Weather Dashboard

A feature-rich weather dashboard built with H2O Wave, providing real-time weather information and forecasts.

## Features

- Real-time weather information
- 5-day weather forecast
- Temperature unit conversion (Celsius/Fahrenheit)
- City search functionality
- Favorite locations
- Responsive design

## Prerequisites

- Python 3.7+
- H2O Wave
- OpenWeatherMap API key

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

4. Create a `.env` file in the root directory and add your OpenWeatherMap API key:
```
OPENWEATHER_API_KEY=your_api_key_here
```

## Running the Application

1. Start the Wave server:
```bash
wave run app.main
```

2. Open your browser and navigate to `http://localhost:10101`

## Running Tests

```bash
pytest tests/
```

## Project Structure

```
weather-app/
├── app/
│   ├── __init__.py
│   ├── main.py      # Main application logic
│   ├── api.py       # API integration
│   └── utils.py     # Utility functions
├── tests/
│   ├── __init__.py
│   └── test_app.py  # Unit tests
├── requirements.txt
└── README.md
```



