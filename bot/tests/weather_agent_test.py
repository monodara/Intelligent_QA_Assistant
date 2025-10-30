# test_weather_assistant.py
import os
import json
import pytest
import dotenv
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import register_tool
from ..tools.weather_tool import WeatherTool  

from qwen_agent.agents import Assistant

dotenv.load_dotenv()

# Register the WeatherTool
register_tool("get_weather")(WeatherTool)

@pytest.fixture(scope="module")
def weather_assistant():
    """Initialize the Assistant that only uses the weather tool"""
    llm_cfg = {
        "model": os.getenv("QWEN_MODEL", "qwen-turbo"),
        "temperature": 0.2,
        "timeout": 30,
        "retry_count": 3,
    }

    assistant = Assistant(
        llm=llm_cfg,
        name="Weather Assistant",
        description="Test assistant that only calls the get_weather tool",
        system_message="You are a helpful assistant. You can call the get_weather tool.",
        function_list=["get_weather"],
    )
    return assistant

@pytest.mark.parametrize("query, expect_keys", [
    ("What's the weather in Berlin tomorrow?", ["success", "location", "date"]),
])
def test_weather_queries(weather_assistant, query, expect_keys):
    """Test weather queries"""
    responses = []
    for r in weather_assistant.run([{"role": "user", "content": query}]):
        # r is a list of messages so we extend it
        responses.extend(r)
    
    # Find the last function call result
    func_response = None
    for r in reversed(responses):
        if r.get("role") == "function" and r.get("name") == "get_weather":
            func_response = json.loads(r["content"])
            break

    assert func_response is not None, "No function response from get_weather"
    
    for key in expect_keys:
        assert key in func_response, f"Expected key {key} in response"
