// src/api.ts
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export interface TripRequest {
  query: string;
  days?: number;
  city?: string;
  data_source?: "offline" | "google";
}

export interface Place {
  name: string;
  category: string;
  description?: string | null;
}

export interface DayPlan {
  day: number;
  places: Place[];
}

export interface TripPlan {
  city: string;
  days: DayPlan[];
  explanation?: string | null;
}

export async function createPlan(req: TripRequest): Promise<TripPlan> {
  const res = await axios.post(`${API_BASE}/plan`, req);
  return res.data;
}
