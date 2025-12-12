# TripWeaver

**Live demo**

- Frontend (React): https://tripweaver-ai.vercel.app/  
- Backend (FastAPI): https://tripweaver.onrender.com  
  - Swagger UI: `https://tripweaver.onrender.com/docs`  
  - Health: `https://tripweaver.onrender.com/health`

---

MCP-orchestrated multi-context **Trip Planner**:

> natural-language → heuristic parser → **LLM parser refine** → POI retrieval (offline / Google) → greedy scoring → Wikipedia enrichment → **LLM explanation layer** → React frontend.

The backend (FastAPI) currently supports:

- Natural-language query parsing  
  - Rule-based heuristic parser  
  - **LLM-refined structured parsing (OpenAI)**
- Two POI data sources  
  - **Offline CSV dataset** (`data/global_poi_dataset.csv`)  
  - **Live Google Places API**
- Scoring + greedy POI selection
- Wikipedia description enrichment
- **Daily pacing control** (relaxed / standard / packed + custom `max_places_per_day`)
- **LLM itinerary explanation** (day-by-day reasoning, alternatives, travel tips)
- JSON itinerary output compatible with the React frontend

---

## 1. Installation

### 1.1 Clone the repository

```bash
git clone https://github.com/Hans-Yin/TripWeaver.git
cd TripWeaver
````

---

### 1.2 Place the offline POI dataset

Your offline dataset must be placed at:

```text
TripWeaver/data/global_poi_dataset.csv
```

Required (or auto-normalizable) columns:

* `city_name`, `place_name`, `country`, `place_category`
* `price`, `open_time`, `close_time`, `popularity_score`
* `lat`, `lon`

Column aliases like `price_usd`, `poi_category`, `latitude`, `longitude` are automatically mapped.

---

### 1.3 Install dependencies

Recommend a virtual environment:

```bash
pip install -r requirements.txt
```

---

### 1.4 Environment variables

#### Google Places API key (optional)

For live POI retrieval:

```bash
export GOOGLE_PLACES_API_KEY="YOUR_GOOGLE_PLACES_API_KEY"
```

#### OpenAI API key (required for LLM parser + LLM explanation layer)

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

Offline mode will still work without these keys (no LLM features / live Google Places).

---

## 2. Run the Backend Server

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

Local API endpoints:

* **Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

CORS is enabled to support the React frontend (local dev & Vercel).

Deployed backend:

* Base URL: `https://tripweaver.onrender.com`
* Swagger UI: `https://tripweaver.onrender.com/docs`
* Health: `https://tripweaver.onrender.com/health`

---

## 3. Request Schema (`POST /plan`)

Example request:

```json
{
  "query": "3 days in New York, love museums and parks, low budget, avoid crowds",
  "days": 3,
  "city": null,
  "data_source": "offline",
  "max_places_per_day": 4,
  "pace": "standard"
}
```

### Field summary

| Field                | Type                     | Description                                                                |
| -------------------- | ------------------------ | -------------------------------------------------------------------------- |
| `query`              | string                   | Free natural-language trip query (city, days, preferences, budget, crowds) |
| `days`               | int (optional)           | Explicit number of days; overrides parser / LLM if provided                |
| `city`               | string | null            | City name; if null, parser + LLM infer from `query`                        |
| `data_source`        | `"offline"` | `"google"` | Choose POI provider                                                        |
| `max_places_per_day` | int (optional)           | Hard cap per day (e.g. 3 for relaxed, 6 for packed)                        |
| `pace`               | string (optional)        | `"relaxed"`, `"standard"`, or `"packed"` (used for UX + LLM explanation)   |

### Backend workflow

1. **Heuristic parser** extracts `city`, `days`, `categories` from `query`
2. **LLM parser refine** converts the query to structured JSON
   (`city`, `total_days`, `categories`, `budget`, `crowd_preference`)
3. Merge explicit `days` from request (if present) with parsed `total_days`
4. Retrieve POIs

   * From **offline CSV**, or
   * From **Google Places API**
5. **Greedy scoring** (popularity + category match)
6. Apply `max_places_per_day` when distributing POIs across days
7. **Wikipedia enrichment** for POI descriptions
8. **LLM explanation layer** generates:

   * Summary of itinerary
   * Day-by-day narrative & pacing
   * Alternative suggestions
   * Travel tips (budget, crowds, timing)
9. Return JSON for frontend rendering

---

## 4. Example Responses

### 4.1 Offline dataset mode

```json
{
  "city": "New York",
  "days": [
    {
      "day": 1,
      "places": [
        {
          "name": "Central Park",
          "category": "park",
          "description": "Central Park is an urban park..."
        },
        {
          "name": "The Metropolitan Museum of Art",
          "category": "museum",
          "description": "The Metropolitan Museum of Art..."
        }
      ]
    },
    {
      "day": 2,
      "places": [
        {
          "name": "Brooklyn Bridge",
          "category": "landmark",
          "description": "The Brooklyn Bridge is..."
        }
      ]
    }
  ],
  "explanation": "This itinerary balances museums and parks while keeping each day at a manageable pace..."
}
```

---

### 4.2 Live Google Places mode

```json
{
  "city": "New York",
  "days": [
    {
      "day": 1,
      "places": [
        {
          "name": "Central Park",
          "category": "park",
          "description": "..."
        },
        {
          "name": "The Metropolitan Museum of Art",
          "category": "museum",
          "description": "..."
        }
      ]
    },
    {
      "day": 2,
      "places": [
        {
          "name": "Brooklyn Museum",
          "category": "museum",
          "description": "..."
        },
        {
          "name": "American Museum of Natural History",
          "category": "museum",
          "description": "..."
        }
      ]
    }
  ],
  "explanation": "This two-day New York itinerary highlights major museums while keeping walking distances reasonable..."
}
```

> Exact POIs may differ depending on Google Places API responses.

---

## 5. React Frontend

The React frontend (Vite) provides a simple UI to:

* Enter natural-language trip queries
* Choose **data source**: offline / Google
* Choose **daily pace**:

  * 🧘 *Relaxed* (~3 spots/day)
  * 🚶 *Standard* (~4 spots/day)
  * ⚡ *Packed* (~6 spots/day)
* Optionally override **max spots/day** via a numeric input
* Toggle **Show LLM explanation**
* Visualize the generated itinerary as a day-by-day timeline

Deployed frontend:

* [https://tripweaver-ai.vercel.app/](https://tripweaver-ai.vercel.app/)

The frontend sends a `POST /plan` request to the FastAPI backend (locally or to the deployed Render endpoint).

If you want to **run the frontend locally against a local FastAPI backend**, you need to update the API endpoint.

### Edit `src/api.ts`

```ts
// src/api.ts

import axios from "axios";

// Use this for deployed backend (default)
const API_BASE = "https://tripweaver.onrender.com";

// Use this for local backend (uncomment when running FastAPI locally)
// const API_BASE = "http://127.0.0.1:8000";
```

### When to change this

| Scenario                        | API_BASE                          |
| ------------------------------- | --------------------------------- |
| Using deployed backend (Render) | `https://tripweaver.onrender.com` |
| Running FastAPI locally         | `http://127.0.0.1:8000`           |

After changing the endpoint, restart the frontend dev server:

```bash
npm run dev
```

This allows the same frontend codebase to work seamlessly with **either the local backend or the deployed backend**.


---

## 6. Contributors

* **Bohan Yin**
* **Nick Chen**
* **Yifei Xu**
