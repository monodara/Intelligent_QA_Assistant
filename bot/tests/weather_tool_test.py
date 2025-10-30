# test_weather_tool_pytest.py
import json
import pytest
from ..tools.weather_tool import WeatherTool 

@pytest.fixture
def weather_tool():
    """Fixture to create a WeatherTool instance."""
    return WeatherTool()

def test_forecast(weather_tool):
    """Test forecast for a date within 7 days (e.g., tomorrow)."""
    params = json.dumps({"location": "Berlin", "date": "tomorrow"})
    res_str = weather_tool.call(params)
    res = json.loads(res_str)

    assert "success" in res
    # check when forecast is successful
    if res["success"]:
        assert "weather" in res or "temp_day" in res
    else:
        # If no data is available, the error field can also provide information
        assert "error" in res

def test_historical_average(weather_tool):
    """Test historical average for a date beyond 7 days (e.g., after two weeks)."""
    params = json.dumps({"location": "Berlin", "date": "after two weeks"})
    res_str = weather_tool.call(params)
    res = json.loads(res_str)

    assert "success" in res
    if res["success"]:
        assert "avg_temp" in res and "avg_humidity" in res
    else:
        assert "error" in res

def test_default_today(weather_tool):
    """Test default behavior with no date (should use today)."""
    params = json.dumps({"location": "Berlin"})
    res_str = weather_tool.call(params)
    res = json.loads(res_str)

    assert "success" in res
    if res["success"]:
        assert "location" in res
    else:
        assert "error" in res
