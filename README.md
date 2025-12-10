# TripWeaver

MCP-orchestrated multi-context **Trip Planner**:
natural-language → heuristic parser → **LLM parser refine** → POI retrieval (offline / Google) → greedy scoring → Wikipedia enrichment → **LLM explanation layer** → React frontend.

The backend (FastAPI) currently supports:

* Natural-language query parsing

  * Rule-based heuristic parser
  * **LLM-refined structured parsing (OpenAI)**
* Two POI data sources

  * **Offline CSV dataset** (`data/global_poi_dataset.csv`)
  * **Live Google Places API**
* Scoring + greedy POI selection
* Wikipedia description enrichment
* **LLM itinerary explanation** (day-by-day reasoning, alternatives, travel tips)
* JSON itinerary output compatible with the React frontend

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Hans-Yin/TripWeaver.git
cd TripWeaver
```

---

## 2. Place the offline POI dataset

Your offline dataset must be placed at:

```
TripWeaver/data/global_poi_dataset.csv
```

Required (or auto-normalizable) columns:

* `city_name`, `place_name`, `country`, `place_category`
* `price`, `open_time`, `close_time`, `popularity_score`
* `lat`, `lon`

Column aliases like `price_usd`, `poi_category`, `latitude`, `longitude` are automatically mapped.

---

## 3. Install dependencies

Recommend a virtual environment:

```bash
pip install -r requirements.txt
```

---

## 4. Environment variables

### Google Places API key (optional)

For live POI retrieval:

```bash
export GOOGLE_PLACES_API_KEY="YOUR_GOOGLE_PLACES_API_KEY"
```

### OpenAI API key (required for LLM parser + LLM explanation layer)

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

Offline mode will still work without these keys.

---

# Run the Backend Server

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

API docs:

* **Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

CORS is enabled to support the React frontend (Vite dev server).

---

# Request Schema (`POST /plan`)

Example request:

```json
{
  "query": "3 days in New York, love museums and parks, low budget, avoid crowds",
  "days": 3,
  "city": null,
  "data_source": "offline"
}
```

### Field summary

| Field         | Type                      | Description                         |
| ------------- | ------------------------- | ----------------------------------- |
| `query`       | string                    | Free natural-language query         |
| `days`        | int (optional)            | Override parser if needed           |
| `city`        | string/null               | Parser will infer city from `query` |
| `data_source` | `"offline"` or `"google"` | Choose data provider                |

### Backend workflow

1. **Heuristic parser** extracts city/days/categories
2. **LLM parser refine** produces structured JSON
3. Retrieve POIs

   * From **offline CSV**, or
   * From **Google Places API**
4. **Greedy scoring** (popularity + category match)
5. **Wikipedia enrichment** for descriptions
6. **LLM explanation layer** generates:

   * Summary of itinerary
   * Day-by-day narrative
   * Alternative suggestions
   * Travel tips (budget, crowds, timing)
7. Return JSON for frontend rendering

---

# Example Responses

## 1. Offline dataset mode

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
  "explanation": "This itinerary balances museums and parks..."
}
```

---

## 2. Live Google Places mode

```json
{
  "city": "New York",
  "days": [
    {
      "day": 1,
      "places": [
        { "name": "Central Park", "category": "park", "description": "..."},
        { "name": "The Metropolitan Museum of Art", "category": "museum", "description": "..."}
      ]
    },
    {
      "day": 2,
      "places": [
        { "name": "Brooklyn Museum", "category": "museum", "description": "..."},
        { "name": "American Museum of Natural History", "category": "museum", "description": "..."}
      ]
    }
  ],
  "explanation": "This two-day New York itinerary highlights..."
}
```

> Results may differ based on Google Places API responses.

---

# React Frontend

A lightweight React interface (Vite) enables users to:

* Enter natural-language trip queries
* Choose data source: offline / Google
* Visualize the generated itinerary
* Read LLM-generated explanations

The frontend and backend communicate via `POST /plan`.

Installation:

```bash
cd frontend
npm install
npm run dev
```

---

# Contributors

* **Bohan Yin**
* **Nick Chen**
* **Yifei Xu**
