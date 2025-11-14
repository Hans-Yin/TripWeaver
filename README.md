# TripWeaver

MCP-orchestrated multi-context Trip Planner: natural-language → parsing → retrieval → planning → constraint checking.  
(Currently implementing backend skeleton with FastAPI; LLM + FAISS + constraint solver coming in next milestones.)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Hans-Yin/TripWeaver.git
cd TripWeaver/backend
````

### 2. Install dependencies

You may use a virtual environment (optional):

```bash
pip install -r requirements.txt
```

---

## Run the Backend Server

Inside the `TripWeaver/backend` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

* **Swagger docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Example Usage

### **POST /plan**

**Request Body:**

```json
{
  "query": "1 day in New York, love landmark and park",
  "days": 1,
  "city": "New York"
}
```

**Response:**

```json
{
  "city": "New York",
  "days": [
    {
      "day": 1,
      "places": [
        {
          "name": "Times Square",
          "category": "landmark",
          "description": null
        },
        {
          "name": "Central Park",
          "category": "park",
          "description": null
        },
        {
          "name": "The Metropolitan Museum of Art",
          "category": "museum",
          "description": null
        },
        {
          "name": "Brooklyn Bridge",
          "category": "landmark",
          "description": null
        }
      ]
    }
  ]
}
```

This is produced by the current **dummy planner** (static placeholder).
In the next steps, this will be replaced with:

* LLM-based preference parser
* POI retrieval (FAISS + metadata store)
* Time-window constraint solver
* Explanation generator

---
## Contributors

*   **Bohan Yin**
    
*   **Nick Chen**
    
*   **Yifei Xu**