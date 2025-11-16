# backend/test_integration.py
"""
End-to-end integration test for parser + planner
"""
from app.schemas import TripRequest, TripPlan
from app.planner import dummy_plan


def test_integration():
    """Test end-to-end flow with sample queries"""
    
    test_cases = [
        TripRequest(query="3 days in Paris visiting museums and parks"),
        TripRequest(query="food and landmarks in New York for 2 days"),
    ]
    
    for req in test_cases:
        print(f"\n{'='*60}")
        print(f"Input Query: {req.query}")
        print(f"{'='*60}")
        
        try:
            trip_plan: TripPlan = dummy_plan(req)
            
            # Validate output format
            assert isinstance(trip_plan, TripPlan), "Output should be TripPlan"
            assert trip_plan.city, "TripPlan should have city"
            assert trip_plan.days, "TripPlan should have days"
            
            print(f"City: {trip_plan.city}")
            print(f"Total Days: {len(trip_plan.days)}")
            
            for day_plan in trip_plan.days:
                print(f"\nDay {day_plan.day}:")
                print(f"  Places ({len(day_plan.places)}):")
                for place in day_plan.places:
                    print(f"    - {place.name} ({place.category})")
            
            print("\n✓ Test passed")
            
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_integration()
