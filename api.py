"""
api.py — Fetch real-time weather data from OpenWeatherMap.
Supports: Current weather + 5-day/3-hour forecast + local CSV fallback.
"""

import os
import requests
import pandas as pd
from typing import Optional, Tuple
from dotenv import load_dotenv
from requests.exceptions import RequestException, Timeout, ConnectionError

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5"


# ─────────────────────────────────────────────────────────────────────────────
# LOCAL CSV FALLBACK
# ─────────────────────────────────────────────────────────────────────────────
def _load_local_csv_as_api(city: str) -> Optional[dict]:
    """Search CWD for a CSV whose filename contains the city name."""
    cwd = os.getcwd()
    for fname in os.listdir(cwd):
        if (
            fname.lower().startswith("weather_data_")
            and fname.lower().endswith(".csv")
            and city.strip().lower() in fname.lower()
        ):
            path = os.path.join(cwd, fname)
            try:
                df = pd.read_csv(path)
            except Exception:
                continue

            list_data = []
            for _, row in df.iterrows():
                try:
                    pop = float(row.get("pop", 0))
                    if pop > 1:
                        pop /= 100.0
                except Exception:
                    pop = 0.0

                list_data.append(
                    {
                        "dt_txt": str(row.get("time", "")),
                        "main": {
                            "temp":     row.get("temp", None),
                            "temp_min": row.get("temp_min", None),
                            "temp_max": row.get("temp_max", None),
                            "humidity": row.get("humidity", None),
                            "pressure": row.get("pressure", None),
                            "feels_like": row.get("feels_like", None),
                        },
                        "wind": {
                            "speed": row.get("wind_speed", None),
                            "deg":   row.get("wind_deg", 0),
                        },
                        "clouds": {"all": row.get("clouds", 0)},
                        "weather": [
                            {
                                "description": row.get("description", ""),
                                "icon": row.get("icon", "01d"),
                            }
                        ],
                        "pop": pop,
                        "visibility": row.get("visibility", 10000),
                    }
                )

            if list_data:
                print(f"  ✔  Loaded local CSV fallback: {fname}")
                return {"city": {"name": city}, "list": list_data}

    return None


# ─────────────────────────────────────────────────────────────────────────────
# CURRENT WEATHER
# ─────────────────────────────────────────────────────────────────────────────
def fetch_current_weather(city: str, api_key: str) -> Optional[dict]:
    """Fetch current-conditions endpoint for rich 'now' stats."""
    params = {
        "q": city,
        "units": "metric",
        "appid": api_key,
    }
    try:
        resp = requests.get(f"{BASE_URL}/weather", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except RequestException:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 5-DAY FORECAST
# ─────────────────────────────────────────────────────────────────────────────
def fetch_forecast(city: str) -> Optional[dict]:
    """
    Fetch 5-day / 3-hour forecast.
    Falls back to local CSV when key is missing or the network fails.
    Returns a dict compatible with extract.extract_data().
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        print("  ⚠  OPENWEATHER_API_KEY not set — trying local CSV fallback.")
        result = _load_local_csv_as_api(city)
        if result is None:
            print("  ✖  No local CSV found for this city either.")
        return result

    params = {
        "q": city,
        "units": "metric",
        "appid": api_key,
        "cnt": 40,  # maximum 5 days
    }

    try:
        resp = requests.get(f"{BASE_URL}/forecast", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print(f"  ✔  Live forecast fetched for '{city}' ({len(data.get('list', []))} slots).")
        return data

    except (Timeout, ConnectionError) as exc:
        print(f"  ⚠  Network error: {exc}")
    except RequestException as exc:
        code = getattr(exc.response, "status_code", "?")
        print(f"  ⚠  API error {code}: {exc}")

    print("  →  Attempting local CSV fallback...")
    result = _load_local_csv_as_api(city)
    if result is None:
        print("  ✖  No suitable local CSV found.")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# COMBINED FETCH (used by main.py)
# ─────────────────────────────────────────────────────────────────────────────
def fetch_all(city: str) -> Tuple[Optional[dict], Optional[dict]]:
    """
    Returns (forecast_data, current_data).
    current_data may be None if key is missing or offline.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    forecast = fetch_forecast(city)
    current = fetch_current_weather(city, api_key) if api_key else None
    return forecast, current