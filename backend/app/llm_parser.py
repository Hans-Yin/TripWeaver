# backend/app/llm_parser.py
from openai import OpenAI
from app.services.llm_client import client, LLM_MODEL

def llm_parse_query(user_query: str) -> dict:
    """
    Use LLM to parse the user's natural language query into structured JSON.
    """
    schema = {
        "name": "TripQuery",
        "schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "total_days": {"type": "integer"},
                "categories": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "budget": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "unspecified"]
                },
                "crowd_preference": {
                    "type": "string",
                    "enum": ["avoid_crowds", "no_preference"]
                }
            },
            "required": ["city", "total_days", "categories"]
        }
    }

    prompt = f"""
You are a travel query parser for TripWeaver.

User query: {user_query}

Extract:
- city name (city)
- number of days (total_days, integer)
- categories of POIs they are interested in (categories, list of strings like "museum", "park", "food", "landmark")
- overall budget (budget: "low", "medium", "high", or "unspecified")
- crowd preference ("avoid_crowds" if they mention avoiding tourists or crowds, otherwise "no_preference").
"""

    response = client.responses.create(
        model=LLM_MODEL,
        input=prompt,
        response_format={
            "type": "json_schema",
            "json_schema": schema
        }
    )

    # The Responses API provides structured output, which is directly JSON.
    parsed = response.output[0].content[0].parsed
    return parsed
