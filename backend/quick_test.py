
<<<<<<< HEAD
from retrieval import load_pois, filter_pois_by_category, top_popular_pois, as_records
=======
from backend.retrieval import load_pois, filter_pois_by_category, top_popular_pois, as_records
>>>>>>> main


def main():
    pois = load_pois() 
    print("Total rows:", len(pois))

    print("\nTop 5 popular in New York:")
    recs = as_records(top_popular_pois(pois, city="newyork", top_k=5))
    for r in recs:
        print(r)

    print("\nCategory filter: entertainment in New York (top 5)")
    recs = as_records(filter_pois_by_category(pois, categories=["entertainment"], city="newyork", top_k=5))
    for r in recs:
        print(r)

if __name__ == "__main__":
    main()

