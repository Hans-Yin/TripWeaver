# backend/app/parser.py
import re
from typing import List, Optional

try:
    from .schemas import TripRequest, ParsedTripRequest
except ImportError:
    # Fallback for standalone execution
    from schemas import TripRequest, ParsedTripRequest

_CATEGORY_ALIASES = {
	"park": ["park", "parks", "parkland"],
	"landmark": ["landmark", "landmarks", "sight", "sights", "sightseeing"],
	"museum": ["museum", "museums", "gallery", "galleries", "art"],
	"food": ["food", "restaurant", "restaurants", "eat", "eating", "cafe", "cafes", "cuisine", "dining", "bar", "bars"],
}


def _normalize_categories(found: List[str]) -> List[str]:
	"""Normalize tokens to canonical categories using aliases map."""
	normalized = []
	for token in found:
		t = token.lower()
		for canon, aliases in _CATEGORY_ALIASES.items():
			if t in aliases or t == canon:
				if canon not in normalized:
					normalized.append(canon)
				break
	return normalized


def parse_query(query: str) -> ParsedTripRequest:
	"""Parse a free-text trip query into inferred preferences.

	Heuristics implemented:
	- detect categories (park, landmark, museum, food) using simple token matching and aliases
	- fallback to ['landmark'] if none detected
	- extract city when phrased like 'in <City>' / 'to <City>' / 'at <City>' / 'near <City>'
	  (simple regex; REQUIRED)
	- extract days when a number is present (prefers phrases like '3 days', falls back to first number)

	Raises: ValueError if no city is detected in the query

	Returns: ParsedTripRequest
	"""
	q = (query or "").strip()

	# 1) categories: look for any alias tokens
	tokens = re.findall(r"[A-Za-z]+", q)
	found = []
	for tok in tokens:
		# quick match against alias lists
		for aliases in _CATEGORY_ALIASES.values():
			if tok.lower() in aliases:
				found.append(tok.lower())
				break

	categories = _normalize_categories(found)
	explicit_categories = True
	if not categories:
		# No explicit category tokens found. Do NOT default to a category when
		# we want 'explicit only' filtering — mark as not explicit and leave list empty.
		explicit_categories = False
		# however keep backward compatibility: parser can still suggest a default
		# category for other consumers if desired. For now, return empty list.
		categories = []

	# 2) days extraction
	days = 1
	m = re.search(r"\b(\d+)\s*(?:days|day|d)\b", q, re.I)
	if m:
		try:
			days = max(1, int(m.group(1)))
		except Exception:
			days = 1
	else:
		# fallback to any standalone number
		m2 = re.search(r"\b(\d+)\b", q)
		if m2:
			try:
				days = max(1, int(m2.group(1)))
			except Exception:
				days = 1

	# 3) city extraction (REQUIRED)
	city: Optional[str] = None
	# catch 'in Paris', 'in New York', 'to Tokyo', 'near Seattle', 'at London'
	city_match = re.search(r"\b(in|to|at|near|around|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", q)

						
	if city_match:
		raw_city = city_match.group(2).strip()
		# remove trailing prepositions if any
		#raw_city = re.sub(r"\s+(for|on|in|at)$", "", raw_city, flags=re.I).strip()
		if raw_city:
			# Title-case city for nicer output
			city = raw_city.title()
	
	# Raise error if city was not detected
	if city is None:
		raise ValueError(f"No city detected in query: '{q}'. Please specify a city using phrases like 'in <City>', 'to <City>', etc.")

	return ParsedTripRequest(query=q, categories=categories, explicit_categories=explicit_categories, city=city, days=days)


if __name__ == "__main__":
	# Simple demo / tests
    samples = [
        "3 days in Paris visiting museums and parks",
        "food and nightlife in New York",
        "things to see in Tokyo",
    ]
    for s in samples:
        parsed = parse_query(s)
        print(f"Query: {s}")
        print(f"Parsed: categories={parsed.categories}, city={parsed.city}, days={parsed.days}")
        print("---")


