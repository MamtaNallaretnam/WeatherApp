# Weather Dashboard

A feature-rich weather dashboard built with H2O Wave, providing real-time weather information and forecasts.

## Features

- Real-time weather information
- 7-day weather forecast
- Temperature unit conversion (Celsius/Fahrenheit)
- City search functionality
- Favorite locations
- Responsive design

## Prerequisites

- Python 3.7+
- H2O Wave

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/weather-app.git
cd weather-app
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

## API Information

This application uses the Open-Meteo API (https://open-meteo.com/) which provides:
- Free weather data
- No API key required
- High accuracy forecasts
- Global coverage
- Generous rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.



