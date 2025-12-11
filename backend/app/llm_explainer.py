# backend/app/llm_explainer.py
from __future__ import annotations

from typing import Optional

from .llm_client import client, LLM_MODEL
from .schemas import TripPlan, TripRequest, ParsedTripRequest


def build_itinerary_explanation(
    req: TripRequest,
    parsed: ParsedTripRequest,
    plan: TripPlan,
) -> str:
    """
    Call LLM to generate a friendly, concise explanation for the itinerary.

    The explanation can include:
    - overall structure of the trip
    - per-day pacing (busy vs relaxed)
    - why these POIs were grouped together
    - suggestions for alternative POIs or detours
    - simple food suggestions near key areas
    - any practical tips (crowds, timing, etc.)
    """
    # JSON version of the final itinerary
    plan_json = plan.model_dump_json()

    user_query = req.query

    prompt = f"""
You are TripWeaver, a smart trip-planning assistant.

The user wrote this original query:
"{user_query}"

We parsed it into this structured preference object:
city = "{parsed.city}"
days = {parsed.days}
categories = {parsed.categories}
data_source = "{getattr(req, "data_source", "offline")}"

Here is the final itinerary in JSON (Pydantic model):
{plan_json}

Please write a friendly, concise explanation of this itinerary for the user.

Requirements:
- 1 short paragraph of overall summary.
- Then for each day, provide a complete and detailed paragraph that:
  * MUST include and mention EVERY single POI/attraction listed for that day in the itinerary,
  * explains the full day's plan in chronological order (morning to evening),
  * describes the rough pace (busy vs relaxed) and timing considerations,
  * explains why these places make sense together geographically and thematically,
  * details any notable transitions between spots (e.g., walking distance, transportation needed),
  * includes practical information like suggested visit duration for each major attraction.
- If helpful, mention:
  * alternative POIs the user could swap in,
  * simple food ideas (e.g., "look for local bakeries near Central Park"),
  * important tips (crowds, opening hours, weather considerations).

Output format:
- Plain text in English.
- No JSON, no markdown, no bullet points. Just paragraphs.
- Use double line breaks (blank line) to separate paragraphs:
  * First paragraph: overall summary
  * Then one paragraph per day (Day 1, Day 2, etc.)
- Each day paragraph should start with "Day X:" or "Day X -" for clarity.
- Ensure no POI from the itinerary is omitted - every attraction must be mentioned in the explanation.
"""

    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful trip-planning assistant called TripWeaver."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    text = resp.choices[0].message.content
    return (text or "").strip()
