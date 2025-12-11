# backend/app/wikipedia.py
import wikipediaapi
import wikipedia
import re

wiki = wikipediaapi.Wikipedia(user_agent='TripWeaver', language='en')


def get_poi_summary(poi_name: str, sentences: int = 3) -> str | None:
    """
    Try to fetch a short Wikipedia summary for a POI name.

    1) Try direct page match via wikipediaapi
    2) If that fails, fall back to wikipedia.search + wikipedia.summary
    3) Truncate to at most `sentences` sentences
    """
    # 1) direct page lookup
    page = wiki.page(poi_name)

    if page.exists():
        summary = page.summary or ""
    else:
        summary = ""

    # 2) fallback: search if direct lookup failed / empty
    if not summary:
        try:
            search_results = wikipedia.search(poi_name)
            if not search_results:
                return None
            page_title = search_results[0]
            summary = wikipedia.summary(page_title, auto_suggest=False)
        except Exception as e:
            print(f"Error fetching Wikipedia summary via search for '{poi_name}': {e}")
            return None

    if not summary:
        return None

    # 3) Limit number of sentences
    if sentences is not None:
        pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        split_sentences = re.split(pattern, summary)
        clipped = " ".join(split_sentences[:sentences])
        summary = clipped

    return summary


def get_wikipedia_summary(query: str, sentences: int = 3) -> str | None:
    """
    Search Wikipedia for a query and return a summary.
    """
    return get_poi_summary(query, sentences=sentences)


# Example usage
if __name__ == "__main__":
    summary = get_wikipedia_summary("Washington Square Park", sentences=3)
    if summary:
        print(summary)
    else:
        print("No Wikipedia summary found for the query.")
