# backend/app/llm_parser.py
from __future__ import annotations

from typing import Dict, Any
import json

from .llm_client import client, LLM_MODEL
from .schemas import ParsedTripRequest


def _extract_json_block(text: str) -> str:
    """
    Try to extract a JSON object string from the LLM response text:
    - find the first '{' and the last '}'
    - extract the middle part

    If failed, just return the original text, let json.loads handle the error.
    """
    if not text:
        return text
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return text
    return text[start : end + 1]


def llm_parse_query(user_query: str) -> Dict[str, Any]:
    """
    Use LLM to parse the user's natural language query into structured JSON.

    Expected output keys:
      - city: str
      - total_days: int
      - categories: list[str]
      - budget: "low" | "medium" | "high" | "unspecified"
      - crowd_preference: "avoid_crowds" | "no_preference"
    """

    system_prompt = """
You are a strict JSON generator for a travel planner called TripWeaver.

Your ONLY job is to read the user's natural language trip query
and return a SINGLE JSON object with the following schema:

{
  "city": string,
  "total_days": integer,
  "categories": [string, ...],   // like "museum", "park", "food", "landmark"
  "budget": "low" | "medium" | "high" | "unspecified",
  "crowd_preference": "avoid_crowds" | "no_preference"
}

Rules:
- Do NOT wrap the JSON in backticks.
- Do NOT include any explanation, text, or comments.
- If a field is not mentioned, guess a reasonable default
  (e.g., budget="unspecified", crowd_preference="no_preference").
"""

    user_prompt = f"User query: {user_query}"

    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    content = resp.choices[0].message.content
    if not content:
        raise RuntimeError("LLM parser returned empty content")

    json_str = _extract_json_block(content)
    try:
        parsed = json.loads(json_str)
    except Exception as e:
        raise RuntimeError(f"Failed to parse LLM JSON: {e}; raw content={content!r}")

    if not isinstance(parsed, dict):
        raise RuntimeError(f"LLM parser did not return a dict: {parsed!r}")

    return parsed


def llm_parse_to_parsed_trip_request(
    user_query: str,
    base: ParsedTripRequest,
) -> ParsedTripRequest:
    """
    Try to refine the heuristic ParsedTripRequest using the LLM parser.

    - If LLM call succeeds, overlay its city/total_days/categories onto `base`.
    - If anything fails (no key, API error, etc.), return `base` unchanged.
    """
    try:
        raw = llm_parse_query(user_query)
    except Exception as e:
        print(f"[LLM parser] Falling back to heuristic parser due to error: {e}")
        return base

    city = (raw.get("city") or "").strip() or base.city

    total_days = raw.get("total_days") or base.days
    try:
        total_days = int(total_days)
        if total_days <= 0:
            total_days = base.days
    except Exception:
        total_days = base.days

    categories = raw.get("categories") or base.categories
    categories = [str(c).strip() for c in categories if str(c).strip()]

    explicit = bool(categories)

    return ParsedTripRequest(
        query=base.query,
        categories=categories,
        explicit_categories=explicit,
        city=city,
        days=total_days,
    )
