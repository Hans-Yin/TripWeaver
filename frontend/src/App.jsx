// src/App.jsx
import React, { useState } from "react";
import "./App.css";
import { createPlan } from "./api";

function App() {
  const [query, setQuery] = useState(
    "3 days in New York, love museums and parks, low budget"
  );
  const [dataSource, setDataSource] = useState("offline"); // "offline" | "google"
  const [useLLM, setUseLLM] = useState(true);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await createPlan({
        query,
        data_source: dataSource,
      });
      setPlan(result);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch plan. Please check backend is running.");
    } finally {
      setLoading(false);
    }
  }

  const hasExplanation = useLLM && plan && plan.explanation;

  return (
    <div className="tw-root">
      {/* top navigation section */}
      <header className="tw-nav">
        <div className="tw-nav-left">
          <span className="tw-logo">TripWeaver</span>
          <span className="tw-tagline">LLM-assisted trip planning</span>
        </div>
        <a
          className="tw-nav-link"
          href="https://github.com/Hans-Yin/TripWeaver"
          target="_blank"
          rel="noreferrer"
        >
          GitHub
        </a>
      </header>

      <main className="tw-main">
        {/* query panel section */}
        <section className="tw-panel">
          <h1 className="tw-title">Describe your dream trip</h1>
          <p className="tw-subtitle">
            Write in natural language. We’ll parse your preferences, pick POIs,
            and explain the itinerary.
          </p>

          <form onSubmit={handleSubmit} className="tw-form">
            <label className="tw-label">
              Trip query
              <textarea
                className="tw-textarea"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={4}
              />
            </label>

            <div className="tw-row">
              <div className="tw-field">
                <span className="tw-label-small">Data source</span>
                <div className="tw-pill-group">
                  <button
                    type="button"
                    className={
                      "tw-pill" +
                      (dataSource === "offline" ? " tw-pill-active" : "")
                    }
                    onClick={() => setDataSource("offline")}
                  >
                    Offline dataset
                  </button>
                  <button
                    type="button"
                    className={
                      "tw-pill" +
                      (dataSource === "google" ? " tw-pill-active" : "")
                    }
                    onClick={() => setDataSource("google")}
                  >
                    Google Places
                  </button>
                </div>
              </div>

              <label className="tw-toggle">
                <input
                  type="checkbox"
                  checked={useLLM}
                  onChange={(e) => setUseLLM(e.target.checked)}
                />
                <span>Show LLM explanation</span>
              </label>
            </div>

            <button
              type="submit"
              className="tw-button"
              disabled={loading || !query.trim()}
            >
              {loading ? "Planning your trip..." : "Generate itinerary"}
            </button>

            {error && <div className="tw-error">{error}</div>}
          </form>

          {/* example chips section */}
          <div className="tw-hints">
            <p className="tw-hints-title">Try examples:</p>
            <button
              className="tw-hint-chip"
              type="button"
              onClick={() =>
                setQuery(
                  "2 days in Paris, love art museums and quiet parks, medium budget"
                )
              }
            >
              Paris • 2 days • art + parks
            </button>
            <button
              className="tw-hint-chip"
              type="button"
              onClick={() =>
                setQuery(
                  "3 days in Tokyo, street food and anime districts, avoid crowds"
                )
              }
            >
              Tokyo • 3 days • food + anime
            </button>
          </div>
        </section>

        {/* result section */}
        <section className="tw-result">
          {!plan && !loading && (
            <div className="tw-empty">
              <h2>Itinerary preview</h2>
              <p>Your day-by-day plan will appear here after you submit.</p>
            </div>
          )}

          {loading && (
            <div className="tw-skeleton">
              <div className="tw-skel-header" />
              <div className="tw-skel-day" />
              <div className="tw-skel-day" />
            </div>
          )}

          {plan && !loading && (
            <>
              {/* summary card section */}
              <div className="tw-summary-card">
                <div>
                  <h2 className="tw-summary-title">
                    {plan.city || "Trip plan"}
                  </h2>
                  <p className="tw-summary-sub">
                    {plan.days?.length || 0} day
                    {plan.days && plan.days.length > 1 ? "s" : ""} itinerary •{" "}
                    {dataSource === "google"
                      ? "Live (Google Places)"
                      : "Offline dataset"}
                  </p>
                </div>
              </div>

              {/* timeline section */}
              <div className="tw-itinerary">
                {(plan.days || []).map((day) => (
                  <div key={day.day} className="tw-day-card">
                    <div className="tw-day-timeline">
                      <div className="tw-day-dot" />
                      <div className="tw-day-line" />
                    </div>

                    <div className="tw-day-content">
                      <h3 className="tw-day-title">Day {day.day}</h3>

                      {(!day.places || day.places.length === 0) && (
                        <p className="tw-day-empty">
                          No POIs found for this day.
                        </p>
                      )}

                      {(day.places || []).map((place, idx) => (
                        <div key={idx} className="tw-place-card">
                          <div className="tw-place-header">
                            <span className="tw-place-name">
                              {place.name}
                            </span>
                            <span
                              className={
                                "tw-badge tw-badge-" +
                                String(place.category || "")
                                  .toLowerCase()
                                  .replace(/\s+/g, "")
                              }
                            >
                              {place.category}
                            </span>
                          </div>
                          {place.description && (
                            <p className="tw-place-desc">
                              {place.description}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* LLM explanation */}
              {hasExplanation && (
                <div className="tw-explain-card">
                  <h3>Why this itinerary works</h3>
                  <p className="tw-explain-text">{plan.explanation}</p>
                  <p className="tw-explain-meta">
                    Generated by LLM based on your preferences and selected
                    POIs.
                  </p>
                </div>
              )}
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
