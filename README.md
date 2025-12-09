# TripWeaver

MCP-orchestrated multi-context Trip Planner: natural-language → parsing → retrieval → scoring → planning.  
Currently we provide a backend skeleton with FastAPI that supports:

- Natural-language query parsing (rule-based parser)
- Two POI data sources:
  - **Offline CSV dataset** (`data/new_global_poi_dataset.csv`)
  - **Live Google Places API**
- Simple scoring + greedy selection of POIs
- JSON itinerary output (days × places)

LLM integration (parser/explanation) and full React frontend will be added later.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Hans-Yin/TripWeaver.git
cd TripWeaver
````

### 2. Place the offline POI dataset

Make sure the CSV file is available at:

```text
TripWeaver/data/global_poi_dataset.csv
```

The file is expected to have (or be normalizable to) the following columns:

* `city_name`, `place_name`, `country`, `place_category`
* `price`, `open_time`, `close_time`, `popularity_score`
* `lat`, `lon`

Column aliases such as `price_usd`, `poi_category`, `latitude`, `longitude` are automatically mapped.

### 3. Install dependencies

You may use a virtual environment (optional):

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Google Places API key

For **live** POI retrieval via Google Places, set the following environment variable:

```bash
export GOOGLE_PLACES_API_KEY="YOUR_GOOGLE_PLACES_API_KEY"
```

Offline mode does **not** require this key.

---

## Run the Backend Server

From the `TripWeaver` project root:

```bash
uvicorn backend.app.main:app --reload
```

The API will be available at:

* **Swagger docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Request Schema

`POST /plan` expects a JSON body matching the `TripRequest` schema:

```json
{
  "query": "2 days in New York visiting museums and parks",
  "days": 2,
  "city": null,
  "data_source": "offline"
}
```

Fields:

* `query` (string, required): free-text trip query (city, days, preferences).
* `days` (int, optional, default = 1): explicit days if you want to override parser.
* `city` (string or null, optional): can be left `null`; parser will infer city from `query`.
* `data_source` (string, optional, default = `"offline"`):

  * `"offline"` → use local CSV dataset (`data/new_global_poi_dataset.csv`)
  * `"google"` → use live Google Places API (requires `GOOGLE_PLACES_API_KEY`)

The backend first parses `query` into a structured `ParsedTripRequest`, then chooses the data source, runs a scoring + greedy selection over candidate POIs, and finally distributes them across days.

---

## Example Usage

### 1. Offline dataset mode

**Request**

```json
POST /plan
{
  "query": "2 days in New York visiting museums and parks",
  "days": 2,
  "city": null,
  "data_source": "offline"
}
```

**Response (example)**

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
          "description": null
        },
        {
          "name": "The Metropolitan Museum of Art",
          "category": "museum",
          "description": null
        }
      ]
    },
    {
      "day": 2,
      "places": [
        {
          "name": "Brooklyn Bridge",
          "category": "landmark",
          "description": null
        },
        {
          "name": "Times Square",
          "category": "landmark",
          "description": null
        }
      ]
    }
  ]
}
```

### 2. Live Google Places mode

**Request**

```json
POST /plan
{
  "query": "2 days in New York visiting museums and parks",
  "days": 2,
  "city": null,
  "data_source": "google"
}
```

**Response (example)**

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
          "description": null
        },
        {
          "name": "The Metropolitan Museum of Art",
          "category": "museum",
          "description": null
        }
      ]
    },
    {
      "day": 2,
      "places": [
        {
          "name": "Brooklyn Museum",
          "category": "museum",
          "description": null
        },
        {
          "name": "American Museum of Natural History",
          "category": "museum",
          "description": null
        }
      ]
    }
  ]
}
```

> Exact POIs may differ depending on the Google Places API response.

---
## Contributors

* **Bohan Yin**
* **Nick Chen**
* **Yifei Xu**