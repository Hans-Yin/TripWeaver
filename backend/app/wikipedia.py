import wikipediaapi
import wikipedia

wiki = wikipediaapi.Wikipedia(user_agent='TripWeaver', language='en')

def get_poi_summary(poi_name: str, sentences: int = 3):
    page = wiki.page(poi_name)

    # Page does not exist
    if not page.exists():
        return None

    summary = page.summary

    # Limit number of sentences
    if sentences is not None:
        summary = ".".join(summary.split(".")[:sentences]).strip() + "."

    return summary


def get_wikipedia_summary(query: str, sentences: int = 3) -> str | None:
    """
    Search Wikipedia for a query and return a summary.

    Args:
        query (str): The search keyword.
        sentences (int): Number of sentences to include in the summary.

    Returns:
        str or None: Summary text if found, otherwise None.
    """
    if get_poi_summary(query, sentences) == None:
        try:
            # Search for pages matching the query
            search_results = wikipedia.search(query)
            if not search_results:
                return None
            # Take the first relevant result
            page_title = search_results[0]

            # Get summary
            summary = wikipedia.summary(page_title, sentences=sentences, auto_suggest=False)
            return summary

        except Exception as e:
            print(f"Error fetching Wikipedia summary: {e}")
            return None


# Example usage
if __name__ == "__main__":
    summary = get_wikipedia_summary("Edge (New York City)", sentences=3)
    if summary:
        print(summary)
    else:
        print("No Wikipedia summary found for the query.")