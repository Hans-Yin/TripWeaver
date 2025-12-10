import { useState } from "react";
import { createPlan } from "./api";

function App() {
  const [query, setQuery] = useState(
    "3 days in New York, love museums and parks, low budget, want to avoid crowds"
  );
  const [days, setDays] = useState("");
  const [city, setCity] = useState("");
  const [dataSource, setDataSource] = useState("offline");
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setPlan(null);

    try {
      const body = {
        query,
        data_source: dataSource,
      };
      if (days) body.days = Number(days);
      if (city) body.city = city;

      const result = await createPlan(body);
      setPlan(result);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch plan. Please check backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", padding: "16px", gap: "16px", fontFamily: "sans-serif" }}>
      {/* Left: query form */}
      <div style={{ flex: "0 0 360px", borderRight: "1px solid #ddd", paddingRight: "16px" }}>
        <h1>TripWeaver</h1>
        <p style={{ color: "#555" }}>
          LLM-powered trip planner: natural language → structured trip plan.
        </p>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "16px" }}>
          <label>
            <div>Trip query</div>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              rows={5}
              style={{ width: "100%" }}
            />
          </label>

          <div style={{ display: "flex", gap: "8px" }}>
            <label style={{ flex: 1 }}>
              Days (optional)
              <input
                type="number"
                min="1"
                value={days}
                onChange={(e) => setDays(e.target.value)}
                style={{ width: "100%" }}
              />
            </label>
            <label style={{ flex: 1 }}>
              City (optional)
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                style={{ width: "100%" }}
                placeholder="New York"
              />
            </label>
          </div>

          <label>
            Data source
            <select
              value={dataSource}
              onChange={(e) => setDataSource(e.target.value)}
              style={{ width: "100%" }}
            >
              <option value="offline">Offline CSV</option>
              <option value="google">Google Places API</option>
            </select>
          </label>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            style={{ marginTop: "8px", padding: "8px 12px" }}
          >
            {loading ? "Planning..." : "Generate Plan"}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: "12px", color: "red" }}>
            {error}
          </div>
        )}
      </div>

      {/* Right: results */}
      <div style={{ flex: 1, paddingLeft: "16px" }}>
        <h2>Itinerary</h2>

        {!plan && !loading && !error && (
          <p style={{ color: "#777" }}>
            Submit a query to see your itinerary here.
          </p>
        )}

        {loading && <p>Planning your trip...</p>}

        {plan && (
          <div style={{ marginTop: "8px" }}>
            <h3>{plan.city}</h3>

            {plan.explanation && (
              <div
                style={{
                  background: "#777",
                  padding: "12px",
                  borderRadius: "6px",
                  marginBottom: "16px",
                  whiteSpace: "pre-line",
                }}
              >
                {plan.explanation}
              </div>
            )}

            {plan.days && plan.days.map((day) => (
              <div
                key={day.day}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: "6px",
                  padding: "12px",
                  marginBottom: "12px",
                }}
              >
                <h4>Day {day.day}</h4>
                {day.places && day.places.length > 0 ? (
                  <ul style={{ paddingLeft: "18px" }}>
                    {day.places.map((place, idx) => (
                      <li key={idx} style={{ marginBottom: "8px" }}>
                        <strong>{place.name}</strong>{" "}
                        <span style={{ color: "#888" }}>({place.category})</span>
                        {place.description && (
                          <div style={{ fontSize: "0.9em", color: "#555", marginTop: "2px" }}>
                            {place.description}
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: "#777" }}>No places for this day.</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
