// src/App.jsx
import React, { useState } from "react";
import "./App.css";
import { createPlan } from "./api";

// Map high-level pace choice to a numeric cap of places per day
const paceToMaxPerDay = {
  relaxed: 3,
  standard: 4,
  packed: 6,
};

function App() {
  // Free-text user query
  const [query, setQuery] = useState(
    "3 days in New York, love museums and parks, low budget"
  );
  // Backend data source mode: offline CSV vs Google Places
  const [dataSource, setDataSource] = useState("offline"); // "offline" | "google"
  // Daily pace: how dense the itinerary should be
  const [pace, setPace] = useState("standard"); // "relaxed" | "standard" | "packed"
  // Optional override: user-defined max spots/day
  const [customMaxPerDay, setCustomMaxPerDay] = useState(""); // string so the input stays controlled
  // Whether to show LLM explanation text (if available)
  const [useLLM, setUseLLM] = useState(true);

  // UI state
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setPlan(null);

    try {
      // Translate pace choice into numeric limit for backend
      let maxPerDay = paceToMaxPerDay[pace] || 4;

      // If user provided a custom value, override the pace-based default
      if (customMaxPerDay) {
        const n = parseInt(customMaxPerDay, 10);
        if (!Number.isNaN(n) && n > 0) {
          maxPerDay = n;
        }
      }

      const result = await createPlan({
        query,
        data_source: dataSource,
        max_places_per_day: maxPerDay,
        pace, // optional: backend / explainer can use this string
      });
      setPlan(result);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch plan. Please check backend is running.");
    } finally {
      setLoading(false);
    }
  }

  // Only show explanation if user enabled it and backend returned it
  const hasExplanation = useLLM && plan && plan.explanation;

  return (
    <div className="tw-root">
      {/* Top navigation bar */}
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
        {/* Left panel: query + controls */}
        <section className="tw-panel">
          <h1 className="tw-title">Describe your dream trip</h1>
          <p className="tw-subtitle">
            Write in natural language. We&apos;ll parse your preferences, pick
            POIs, and explain the itinerary.
          </p>

          <form onSubmit={handleSubmit} className="tw-form">
            {/* Query input */}
            <label className="tw-label">
              Trip query
              <textarea
                className="tw-textarea"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={4}
              />
            </label>

            {/* Row: data source + daily pace selector */}
            <div className="tw-row">
              {/* Data source toggle */}
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

              {/* Daily pace buttons */}
              <div className="tw-field">
                <span className="tw-label-small">Daily pace</span>
                <div className="pace-toggle">
                  <button
                    type="button"
                    className={
                      "pace-btn" + (pace === "relaxed" ? " active" : "")
                    }
                    onClick={() => setPace("relaxed")}
                  >
                    🧘 Relaxed
                    <span className="pace-caption">~3 spots / day</span>
                  </button>
                  <button
                    type="button"
                    className={
                      "pace-btn" + (pace === "standard" ? " active" : "")
                    }
                    onClick={() => setPace("standard")}
                  >
                    🚶 Standard
                    <span className="pace-caption">~4 spots / day</span>
                  </button>
                  <button
                    type="button"
                    className={
                      "pace-btn" + (pace === "packed" ? " active" : "")
                    }
                    onClick={() => setPace("packed")}
                  >
                    ⚡ Packed
                    <span className="pace-caption">~6 spots / day</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Optional custom max spots/day */}
            <div className="tw-row tw-row-bottom">
              <div className="tw-field">
                <span className="tw-label-small">
                  Custom max spots / day (optional)
                </span>
                <input
                  type="number"
                  min={1}
                  max={12}
                  className="tw-number-input"
                  placeholder="e.g. 5"
                  value={customMaxPerDay}
                  onChange={(e) => setCustomMaxPerDay(e.target.value)}
                />
              </div>

              {/* LLM explanation toggle */}
              <label className="tw-toggle">
                <input
                  type="checkbox"
                  checked={useLLM}
                  onChange={(e) => setUseLLM(e.target.checked)}
                />
                <span>Show LLM explanation</span>
              </label>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              className="tw-button"
              disabled={loading || !query.trim()}
            >
              {loading ? "Planning your trip..." : "Generate itinerary"}
            </button>

            {/* Error message */}
            {error && <div className="tw-error">{error}</div>}
          </form>

          {/* Example queries as clickable chips */}
          <div className="tw-hints">
            <p className="tw-hints-title">Try examples:</p>
            <button
              className="tw-hint-chip"
              type="button"
              onClick={() =>
                setQuery(
                  "2 days in Paris, love art museums and quiet parks, medium budget, relaxed pace"
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
                  "3 days in Tokyo, street food and anime districts, avoid crowds, packed schedule"
                )
              }
            >
              Tokyo • 3 days • food + anime
            </button>
            <button
              className="tw-hint-chip"
              type="button"
              onClick={() =>
                setQuery(
                  "4 days in Rome, history-focused trip with some relaxed evenings in local neighborhoods"
                )
              }
            >
              Rome • 4 days • history + local
            </button>
          </div>
        </section>

        {/* Right panel: itinerary + explanation */}
        <section className="tw-result">
          {/* Empty state before first query */}
          {!plan && !loading && (
            <div className="tw-empty">
              <h2>Itinerary preview</h2>
              <p>Your day-by-day plan will appear here after you submit.</p>
            </div>
          )}

          {/* Loading skeleton */}
          {loading && (
            <div className="tw-skeleton">
              <div className="tw-skel-header" />
              <div className="tw-skel-day" />
              <div className="tw-skel-day" />
            </div>
          )}

          {/* Render itinerary when available */}
          {plan && !loading && (
            <>
              {/* Summary card */}
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
                      : "Offline dataset"}{" "}
                    •{" "}
                    {pace === "relaxed"
                      ? "relaxed pace"
                      : pace === "packed"
                      ? "packed pace"
                      : "standard pace"}
                  </p>
                </div>
              </div>

              {/* Timeline of days and places */}
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
                            <span className="tw-place-name">{place.name}</span>
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
                            <p className="tw-place-desc">{place.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* LLM explanation panel */}
              {hasExplanation && (
                <div className="tw-explain-card">
                  <h3>Why this itinerary works</h3>
                  <div className="tw-explain-text">
                    {plan.explanation.split("\n\n").map((paragraph, idx) => (
                      <p key={idx} className="tw-explain-paragraph">
                        {paragraph.trim()}
                      </p>
                    ))}
                  </div>
                  <p className="tw-explain-meta">
                    Generated by an LLM based on your preferences and the
                    selected POIs.
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
