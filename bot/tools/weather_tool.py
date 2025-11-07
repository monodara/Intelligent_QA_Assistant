import os
import json
import requests
import dateparser
from datetime import datetime, timezone
from typing import Optional
from langchain_core.tools import tool
import dotenv

from ..core.ollama_handler import generate_local_answer

dotenv.load_dotenv()

# Module-level state
API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
if not API_KEY:
    raise ValueError("Please set environment variable OPENWEATHER_API_KEY")
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
FORECAST_URL = "https://api.openweathermap.org/data/3.0/onecall"
HISTORY_URL = "https://api.openweathermap.org/data/3.0/onecall/timemachine"

def _parse_date(date_str: Optional[str]) -> datetime:
    """Parse natural language or explicit date string."""
    if not date_str:
        return datetime.today()
    parsed = dateparser.parse(date_str, languages=["en"])
    return parsed if parsed else datetime.today()

def _get_coords(location: str):
    """Get latitude and longitude for a city."""
    resp = requests.get(GEOCODE_URL, params={"q": location, "limit": 1, "appid": API_KEY}, timeout=10).json()
    if not resp:
        raise ValueError(f"Cannot find city: {location}")
    return resp[0]["lat"], resp[0]["lon"]

def _fetch_forecast(lat: float, lon: float, target_utc_date: datetime.date, location: str) -> dict:
    """
    Fetch forecast from OpenWeather API for dates within the next 7 days.
    Returns forecast dict or error dict.
    """
    resp = requests.get(FORECAST_URL, params={
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,hourly,alerts",
        "units": "metric",
        "appid": API_KEY
    }, timeout=10).json()

    daily_list = resp.get("daily", [])

    for day in daily_list:
        day_date = datetime.fromtimestamp(day["dt"], tz=timezone.utc).date()
        if day_date == target_utc_date:
            return {
                "success": True,
                "source": "forecast",
                "location": location,
                "date": target_utc_date.strftime("%Y-%m-%d"),
                "weather": day["weather"][0]["description"],
                "temp_day": day["temp"]["day"],
                "temp_night": day["temp"]["night"],
                "humidity": day["humidity"],
                "wind_speed": day["wind_speed"]
            }
    return {"success": False, "error": "No forecast data available for this date."}

def _get_historical_average(lat, lon, target_date: datetime, location: str):
    """Get historical averages by checking same date in past 3 years."""
    temps, humidities, weathers = [], [], []
    for year in range(1, 4):
        past_date = target_date.replace(year=target_date.year - year)
        timestamp = int(past_date.timestamp())
        resp = requests.get(HISTORY_URL, params={
            "lat": lat, "lon": lon, "dt": timestamp, "units": "metric", "appid": API_KEY
        }, timeout=10).json()
        if resp.get("data"):
            c = resp["data"][0]
            temps.append(c["temp"])
            humidities.append(c["humidity"])
            if c.get("weather"):
                weathers.append(c["weather"][0]["description"])

    if not temps:
        return {"success": False, "error": "No historical data available"}

    avg_temp = sum(temps) / len(temps)
    avg_humidity = sum(humidities) / len(humidities)
    common_weather = max(set(weathers), key=weathers.count) if weathers else "Unknown"

    return {
        "success": True,
        "source": "historical_average",
        "location": location,
        "date": target_date.strftime("%Y-%m-%d"),
        "avg_temp": f"{avg_temp:.1f}°C",
        "avg_humidity": f"{avg_humidity:.0f}%",
        "typical_weather": common_weather,
        "note": "Forecast unavailable; showing average climate for same date in past 3 years."
    }

@tool
def get_weather(location: str, date: Optional[str] = None) -> str:
    """Get current or forecast weather, or historical averages for a specific city and date."""
    print("get_weather tool called with location:", location, "and date:", date)
    
    target_date = _parse_date(date)
    print("Parsed target date:", target_date)
    lat, lon = _get_coords(location)
    print("Parsed coordinates:", lat, lon)

    target_utc_date = target_date.astimezone(timezone.utc).date()
    today_utc = datetime.now(timezone.utc).date()
    delta_days = (target_utc_date - today_utc).days

    if delta_days < 0:
        result = {"success": False, "error": "Past dates are not supported."}
    elif delta_days <= 7:
        result = _fetch_forecast(lat, lon, target_utc_date, location)
    else:
        result = _get_historical_average(lat, lon, target_date, location)
    print("Weather tool result:", result)
    return result
