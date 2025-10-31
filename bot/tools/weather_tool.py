import os
import json
import requests
import dateparser
from datetime import datetime, timezone
from typing import Optional
from qwen_agent.tools.base import BaseTool, register_tool
import dotenv

from ..core.ollama_handler import generate_local_answer

dotenv.load_dotenv()


class WeatherTool(BaseTool):
    """
    Retrieve weather information for a given location and date.
    If the date is too far in the future (beyond 7 days), returns historical averages.
    """
    name = "get_weather"
    description = "Get current or forecast weather, or historical averages for a specific city and date."
    parameters = [
        {"name": "location", "type": "string", "description": "City name, e.g., Berlin", "required": True},
        {"name": "date", "type": "string", "description": "Date or natural phrase (e.g., 'today', 'in 2 months', '2025-12-10')", "required": False},
    ]

    def __init__(self, cfg=None):
        self.cfg = cfg
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')
        if not self.api_key:
            raise ValueError("Please set environment variable OPENWEATHER_API_KEY")
        self.geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.forecast_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.history_url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"

    def parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse natural language or explicit date string."""
        if not date_str:
            return datetime.today()
        parsed = dateparser.parse(date_str, languages=["en", "zh"])
        return parsed if parsed else datetime.today()

    def get_coords(self, location: str):
        """Get latitude and longitude for a city."""
        resp = requests.get(self.geocode_url, params={"q": location, "limit": 1, "appid": self.api_key}, timeout=10).json()
        if not resp:
            raise ValueError(f"Cannot find city: {location}")
        return resp[0]["lat"], resp[0]["lon"]

    def _fetch_forecast(self, lat: float, lon: float, target_utc_date: datetime.date, location: str) -> dict:
        """
        Fetch forecast from OpenWeather API for dates within the next 7 days.
        Returns forecast dict or error dict.
        """
        resp = requests.get(self.forecast_url, params={
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,hourly,alerts",
            "units": "metric",
            "appid": self.api_key
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

    def get_historical_average(self, lat, lon, target_date: datetime, location: str):
        """Get historical averages by checking same date in past 3 years."""
        temps, humidities, weathers = [], [], []
        for year in range(1, 4):
            past_date = target_date.replace(year=target_date.year - year)
            timestamp = int(past_date.timestamp())
            resp = requests.get(self.history_url, params={
                "lat": lat, "lon": lon, "dt": timestamp, "units": "metric", "appid": self.api_key
            }, timeout=10).json()
            if "current" in resp:
                c = resp["current"]
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

    def call(self, params: str, **kwargs) -> str:
        """
        Get weather for a given location and date.
        - For dates within next 7 days, use forecast.
        - For dates beyond 7 days, use historical average.
        """
        print("WeatherTool call with params:", params)
        args = json.loads(params)
        print("WeatherTool called with args:", args)
        location = args['location']
        date_str = args.get('date', None)

        # parse date 
        target_date = self.parse_date(date_str)
        lat, lon = self.get_coords(location)

        # get UTC date
        target_utc_date = target_date.astimezone(timezone.utc).date()
        today_utc = datetime.now(timezone.utc).date()
        delta_days = (target_utc_date - today_utc).days

        # check date range and fetch data
        if delta_days < 0:
            result = {"success": False, "error": "Past dates are not supported."}
        elif delta_days <= 7:
            # use forecast
            result = self._fetch_forecast(lat, lon, target_utc_date, location)
        else:
            # use historical average
            result = self.get_historical_average(lat, lon, target_date, location)


        prompt = f"""
                You are an expert weather analyst. Change the weather JSON to natural language answer for the user.
                - Return ONLY a concise, natural-language weather report.
                - DO NOT include greeting phrases.
                - The output should start directly with the weather sentence.

                location: "{location}"
                date: "{target_date.strftime('%Y-%m-%d')}"
                The weather data returned as follows:
                {result}

                Answer:
                """
        answer = generate_local_answer(prompt)
        return {
                "success": True,
                "answer": answer,
            }

