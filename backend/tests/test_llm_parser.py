# backend/tests/test_llm_parser.py
from backend.app.llm_parser import llm_parse_query, llm_parse_to_parsed_trip_request
from backend.app.parser import parse_query


def main():
    user_query = "I want a long weekend trip somewhere in China, maybe Shanghai or Beijing, love museums and parks, low budget, want to avoid crowds."

    # 1) original heuristic parser
    base = parse_query(user_query)
    print("=== Heuristic parse ===")
    print(base)
    print()

    # 2) LLM refine
    refined = llm_parse_to_parsed_trip_request(user_query, base)
    print("=== LLM-refined parse ===")
    print(refined)
    print()

    # 3) raw JSON (optional)
    raw = llm_parse_query(user_query)
    print("=== Raw LLM JSON ===")
    print(raw)


if __name__ == "__main__":
    main()
