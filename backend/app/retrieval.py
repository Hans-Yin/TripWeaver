
from __future__ import annotations
import pandas as pd
from typing import Iterable, List, Optional, Dict

REQUIRED_COLS = [
    "city_name", "place_name", "country", "place_category",
    "price", "open_time", "close_time", "popularity_score", "lat", "lon"
]

def load_pois(csv_path: str = "../data/new_global_poi_dataset.csv") -> pd.DataFrame:
  
    df = pd.read_csv(csv_path)
    # handle alternate column names (if any drifted)
    # try to coerce common variants
    col_alias = {
        "price_usd": "price",
        "open_time_min": "open_time",
        "close_time_min": "close_time",
        "poi_category": "place_category",
        "latitude": "lat",
        "longitude": "lon",
    }
    for src, dst in col_alias.items():
        if src in df.columns and dst not in df.columns:
            df.rename(columns={src: dst}, inplace=True)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Found: {list(df.columns)}")

    # normalize types
    numeric_cols = ["price", "open_time", "close_time", "popularity_score"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # lat/lon can be strings like “40.7309° N”, “73.9973° W”.
    # convert to signed floats while preserving original columns too.
    def _to_float_deg(v):
        if pd.isna(v):
            return None
        s = str(v).strip()
        # if plain float, just return
        try:
            return float(s)
        except:
            pass
        # handle forms like “40.7309° N” or “73.9973° W”
        s = s.replace("°", "").replace("º", "").replace("ﹾ", "").strip()
        parts = s.split()
        if len(parts) == 2:
            val, hemi = parts
            try:
                val = float(val)
            except:
                return None
            hemi = hemi.upper()
            if hemi in ("S", "W"):
                val = -abs(val)
            else:
                val = abs(val)
            return val
        # fallback
        return None

    if df["lat"].dtype == object:
        df["lat_float"] = df["lat"].map(_to_float_deg)
    else:
        df["lat_float"] = df["lat"].astype(float)

    if df["lon"].dtype == object:
        df["lon_float"] = df["lon"].map(_to_float_deg)
    else:
        df["lon_float"] = df["lon"].astype(float)

   
    df = df.dropna(subset=["popularity_score"])
    return df


def filter_pois_by_category(
    pois: pd.DataFrame,
    categories: Optional[Iterable[str]] = None,
    city: Optional[str] = None,
    top_k: int = 10,
) -> pd.DataFrame:

    df = pois

    if city:
        df = df[df["city_name"].str.lower() == city.strip().lower()]

    if categories:
        cats = {c.strip().lower() for c in categories if c and str(c).strip()}
        if cats:
            df = df[df["place_category"].str.lower().isin(cats)]

    # If no categories provided (or none matched), fall back to top popular
    if categories is None or len(df) == 0:
        df = pois if city is None else pois[pois["city_name"].str.lower() == city.strip().lower()]

    df = df.sort_values(["popularity_score", "price"], ascending=[False, True]).head(top_k)
    return df.reset_index(drop=True)


def top_popular_pois(
    pois: pd.DataFrame,
    city: Optional[str] = None,
    top_k: int = 10
) -> pd.DataFrame:
    return filter_pois_by_category(pois, categories=None, city=city, top_k=top_k)


def as_records(df: pd.DataFrame) -> List[Dict]:
    
    keep = [
        "city_name", "place_name", "country", "place_category",
        "price", "open_time", "close_time", "popularity_score",
        "lat", "lon", "lat_float", "lon_float"
    ]
    keep = [k for k in keep if k in df.columns]
    return df[keep].to_dict(orient="records")
