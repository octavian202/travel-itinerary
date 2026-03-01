"""
AI-generated itinerary via OpenAI Chat Completions API.

Returns a day-by-day list of stops (name, category, estimated_duration_minutes)
using structured JSON output. Requires OPENAI_API_KEY in the environment.
"""

import logging
import os
from dataclasses import dataclass

from openai import OpenAI

logger = logging.getLogger(__name__)

# JSON schema for structured output: days with stops (name, category, estimated_duration_minutes)
ITINERARY_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "days": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "day_number": {"type": "integer"},
                    "stops": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "category": {"type": "string"},
                                "estimated_duration_minutes": {"type": "integer"},
                            },
                            "required": ["name", "category", "estimated_duration_minutes"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["day_number", "stops"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["days"],
    "additionalProperties": False,
}


@dataclass
class AIStop:
    """Single stop suggested by the AI."""
    name: str
    category: str
    estimated_duration_minutes: int


@dataclass
class AIDay:
    """One day of the itinerary."""
    day_number: int
    stops: list[AIStop]


@dataclass
class AIItineraryResult:
    """Full AI-generated itinerary."""
    days: list[AIDay]


def _parse_structured_response(content: str) -> AIItineraryResult | None:
    """Parse the JSON content from the model into typed structures."""
    import json
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning("AI response not valid JSON: %s", e)
        return None
    days_raw = data.get("days")
    if not isinstance(days_raw, list):
        return None
    days: list[AIDay] = []
    for d in days_raw:
        if not isinstance(d, dict):
            continue
        day_num = d.get("day_number")
        stops_raw = d.get("stops")
        if day_num is None or not isinstance(stops_raw, list):
            continue
        stops: list[AIStop] = []
        for s in stops_raw:
            if not isinstance(s, dict):
                continue
            name = s.get("name")
            category = s.get("category")
            duration = s.get("estimated_duration_minutes")
            if name is None or category is None or duration is None:
                continue
            stops.append(
                AIStop(
                    name=str(name)[:255],
                    category=str(category)[:64],
                    estimated_duration_minutes=int(duration),
                )
            )
        if stops:
            days.append(AIDay(day_number=int(day_num), stops=stops))
    if not days:
        return None
    return AIItineraryResult(days=days)


def generate_ai_itinerary(
    city_name: str,
    days: int,
    pace: str,
) -> AIItineraryResult | None:
    """
    Call OpenAI API to generate a multi-day itinerary for the given city.

    pace: "relaxed" | "moderate" | "fast"
    - relaxed: 2-3 activities per day
    - moderate: 4-5 per day
    - fast: 6+ per day

    Returns None if the API key is missing, the call fails, or the response is invalid.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in the environment.")

    activities_per_day = {"relaxed": "2 to 3", "moderate": "4 to 5", "fast": "6 or more"}
    num_activities = activities_per_day.get(pace, "4 to 5")

    system_prompt = (
        "You are a travel planner. Generate a day-by-day itinerary of real, specific "
        "attractions, museums, landmarks, parks, and restaurants in the given city. "
        "Use the exact response format requested (JSON with days and stops). "
        "Each stop must have name (specific place name), category (e.g. museum, park, restaurant), "
        "and estimated_duration_minutes (integer, typically 30-120). "
        "Suggest well-known, geocodable places so they can be found on a map."
    )
    user_prompt = (
        f"Create a {days}-day itinerary for {city_name} with a {pace} pace. "
        f"Include {num_activities} activities per day. "
        f"Return exactly {days} days, each with day_number (1 to {days}) and a list of stops "
        "with name, category, and estimated_duration_minutes."
    )

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "itinerary",
                    "strict": True,
                    "schema": ITINERARY_JSON_SCHEMA,
                },
            },
        )
    except Exception as e:
        logger.warning("OpenAI API call failed: %s", e)
        return None

    choice = response.choices[0] if response.choices else None
    if not choice or not getattr(choice, "message", None):
        return None
    content = choice.message.content
    if not content:
        return None
    return _parse_structured_response(content)
