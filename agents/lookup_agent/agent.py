"""Lookup Agent - Headless A2A service for data lookups."""

import os
from datetime import datetime, timezone

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a


# Simulated data for demonstration
WEATHER_DATA = {
    "new york": {"temp": 72, "condition": "Sunny", "humidity": 45},
    "london": {"temp": 58, "condition": "Cloudy", "humidity": 70},
    "tokyo": {"temp": 68, "condition": "Partly Cloudy", "humidity": 55},
    "sydney": {"temp": 75, "condition": "Clear", "humidity": 40},
    "paris": {"temp": 62, "condition": "Rainy", "humidity": 80},
}

TIMEZONE_OFFSETS = {
    "new york": -5,
    "london": 0,
    "tokyo": 9,
    "sydney": 11,
    "paris": 1,
    "los angeles": -8,
}


def get_weather(city: str) -> dict:
    """Get current weather for a city.

    Args:
        city: Name of the city

    Returns:
        Dictionary with weather information
    """
    city_lower = city.lower()
    if city_lower in WEATHER_DATA:
        data = WEATHER_DATA[city_lower]
        return {
            "city": city,
            "temperature_f": data["temp"],
            "condition": data["condition"],
            "humidity_percent": data["humidity"],
            "status": "success",
        }
    return {
        "city": city,
        "status": "not_found",
        "message": f"Weather data not available for {city}. Available cities: {', '.join(WEATHER_DATA.keys())}",
    }


def get_timezone(city: str) -> dict:
    """Get timezone information for a city.

    Args:
        city: Name of the city

    Returns:
        Dictionary with timezone and current time
    """
    city_lower = city.lower()
    if city_lower in TIMEZONE_OFFSETS:
        offset = TIMEZONE_OFFSETS[city_lower]
        utc_now = datetime.now(timezone.utc)
        local_hour = (utc_now.hour + offset) % 24
        return {
            "city": city,
            "utc_offset": offset,
            "current_time": f"{local_hour:02d}:{utc_now.minute:02d}",
            "status": "success",
        }
    return {
        "city": city,
        "status": "not_found",
        "message": f"Timezone data not available for {city}. Available cities: {', '.join(TIMEZONE_OFFSETS.keys())}",
    }


root_agent = Agent(
    model="gemini-2.0-flash",
    name="lookup_agent",
    description="Agent specialized in data lookups including weather information and timezone data.",
    instruction="""You are a data lookup assistant.
    Use the provided tools to retrieve information.
    Present the data in a clear, formatted manner.""",
    tools=[get_weather, get_timezone],
)

# Create A2A-compatible app
PORT = int(os.environ.get("PORT", 8002))
# Use AGENT_HOST env var for Docker networking, defaults to localhost for local dev
AGENT_HOST = os.environ.get("AGENT_HOST", "localhost")

# Create custom agent card with correct URL for Docker networking
agent_card = AgentCard(
    name="lookup_agent",
    description=root_agent.description,
    url=f"http://{AGENT_HOST}:{PORT}",
    version="1.0.0",
    capabilities=AgentCapabilities(),
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    skills=[
        AgentSkill(
            id="data_lookups",
            name="Data Lookups",
            description="Retrieve weather information and timezone data for cities",
            tags=["lookup", "weather", "timezone"],
        )
    ],
)

a2a_app = to_a2a(root_agent, port=PORT, agent_card=agent_card)
