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

## Screenshots
![image](https://github.com/user-attachments/assets/065b8710-fe50-42d4-ab65-739211f51240)
![image](https://github.com/user-attachments/assets/2e182f2d-f3e0-4508-a088-4118b0adb70b)
![image](https://github.com/user-attachments/assets/a3c8254e-0e43-4da5-b507-6a5458592184)
![image](https://github.com/user-attachments/assets/70b12d55-e663-4181-bad5-acea1e83975a)
![image](https://github.com/user-attachments/assets/be16232b-ae6a-4c78-ab09-12d61e48b264)
![image](https://github.com/user-attachments/assets/2545e79a-7bdb-4ad2-b665-d511db143a3b)

## demo-video
https://drive.google.com/file/d/1c29WVi9T8An1C3YKAjmAHQo5Y_Bz8-KA/view?usp=sharing


## API Information

This application uses the Open-Meteo API (https://open-meteo.com/) which provides:
- Free weather data
- No API key required
- High accuracy forecasts
- Global coverage
- Generous rate limits





