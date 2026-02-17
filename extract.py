import math
import pandas as pd
from typing import Tuple, Optional, Dict


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _heat_index(temp_c: float, rh: float) -> float:
    t = temp_c * 9 / 5 + 32  # °F
    hi = (
        -42.379
        + 2.04901523 * t
        + 10.14333127 * rh
        - 0.22475541 * t * rh
        - 0.00683783 * t**2
        - 0.05481717 * rh**2
        + 0.00122874 * t**2 * rh
        + 0.00085282 * t * rh**2
        - 0.00000199 * t**2 * rh**2
    )
    return (hi - 32) * 5 / 9  # back to °C


def _wind_chill(temp_c: float, wind_kmh: float) -> float:
    return (
        13.12
        + 0.6215 * temp_c
        - 11.37 * wind_kmh**0.16
        + 0.3965 * temp_c * wind_kmh**0.16
    )


def _dew_point(temp_c: float, rh: float) -> float:
    a, b = 17.27, 237.7
    gamma = (a * temp_c / (b + temp_c)) + math.log(rh / 100.0)
    return (b * gamma) / (a - gamma)


def _safe(val, fallback=0.0):
    try:
        return float(val) if val is not None else fallback
    except (TypeError, ValueError):
        return fallback


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXTRACT
# ─────────────────────────────────────────────────────────────────────────────
def extract_data(data: Dict) -> Tuple[pd.DataFrame, str]:
    """
    Convert raw OpenWeatherMap forecast JSON → (DataFrame, city_name).

    Required columns in output DataFrame:
        time, temp, temp_min, temp_max, feels_like,
        humidity, pressure, wind_speed, wind_deg,
        pop, clouds, description, icon,
        heat_index, wind_chill, dew_point,
        day_label, hour_label
    """
    list_data = data.get("list", [])
    city = data.get("city", {}).get("name", "Unknown City")

    if not list_data:
        print("  ✖  No forecast entries in API response.")
        return pd.DataFrame(), city

    rows = []
    for item in list_data:
        main = item.get("main", {})
        wind = item.get("wind", {})
        weather_arr = item.get("weather", [{}])
        weather_desc = weather_arr[0] if weather_arr else {}

        temp        = _safe(main.get("temp"))
        feels_like  = _safe(main.get("feels_like", temp))
        temp_min    = _safe(main.get("temp_min", temp))
        temp_max    = _safe(main.get("temp_max", temp))
        humidity    = _safe(main.get("humidity", 0))
        pressure    = _safe(main.get("pressure", 1013))
        wind_speed  = _safe(wind.get("speed", 0))          # m/s
        wind_deg    = _safe(wind.get("deg", 0))
        clouds      = _safe(item.get("clouds", {}).get("all", 0))
        raw_pop     = _safe(item.get("pop", 0))
        pop         = raw_pop * 100 if raw_pop <= 1 else raw_pop  # store as %
        visibility  = _safe(item.get("visibility", 10000)) / 1000  # km
        desc        = weather_desc.get("description", "")
        icon        = weather_desc.get("icon", "01d")

        # ── computed ──────────────────────────────────────────────────────────
        wind_kmh = wind_speed * 3.6
        if temp >= 27 and humidity >= 40:
            hi = _heat_index(temp, humidity)
        else:
            hi = temp

        if temp <= 10 and wind_kmh >= 4.8:
            wc = _wind_chill(temp, wind_kmh)
        else:
            wc = temp

        dp = _dew_point(temp, max(humidity, 1))

        rows.append(
            {
                "time":        item.get("dt_txt", ""),
                "temp":        round(temp, 1),
                "temp_min":    round(temp_min, 1),
                "temp_max":    round(temp_max, 1),
                "feels_like":  round(feels_like, 1),
                "humidity":    round(humidity, 1),
                "pressure":    round(pressure, 1),
                "wind_speed":  round(wind_speed, 2),
                "wind_kmh":    round(wind_kmh, 1),
                "wind_deg":    round(wind_deg, 0),
                "pop":         round(pop, 1),
                "clouds":      round(clouds, 0),
                "visibility":  round(visibility, 2),
                "description": desc,
                "icon":        icon,
                "heat_index":  round(hi, 1),
                "wind_chill":  round(wc, 1),
                "dew_point":   round(dp, 1),
            }
        )

    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)

    # label helpers for charts
    df["day_label"]  = df["time"].dt.strftime("%a %d %b")
    df["hour_label"] = df["time"].dt.strftime("%H:%M")
    df["datetime_str"] = df["time"].dt.strftime("%a %d %b %H:%M")

    print(
        f"  ✔  Extracted {len(df)} rows for '{city}' "
        f"({df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()})"
    )
    return df, city


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY STATS (used by terminal report + dashboard)
# ─────────────────────────────────────────────────────────────────────────────
def compute_summary(df: pd.DataFrame) -> Dict:
    if df.empty:
        return {}

    return {
        "temp_avg":      round(df["temp"].mean(), 1),
        "temp_max":      round(df["temp_max"].max(), 1),
        "temp_min":      round(df["temp_min"].min(), 1),
        "humidity_avg":  round(df["humidity"].mean(), 1),
        "pressure_avg":  round(df["pressure"].mean(), 1),
        "wind_max":      round(df["wind_speed"].max(), 2),
        "pop_max":       round(df["pop"].max(), 1),
        "dew_point_avg": round(df["dew_point"].mean(), 1),
        "total_slots":   len(df),
        "days_covered":  df["time"].dt.date.nunique(),
    }

