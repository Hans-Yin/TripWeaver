# backend/app/main.py
from fastapi import FastAPI
from .schemas import TripRequest, TripPlan
from .planner import dummy_plan

app = FastAPI(title="TripWeaver API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/plan", response_model=TripPlan)
def create_plan(req: TripRequest):
    # Now using dummy planner, will replace it with actual MCP / LLM pipeline later.
    plan = dummy_plan(req)
    return plan
