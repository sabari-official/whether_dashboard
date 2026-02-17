import sys
import os
import argparse
from datetime import datetime

from api import fetch_all
from extract import extract_data, compute_summary
from dashboard import dashboard_plot

# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL COLOURS
# ─────────────────────────────────────────────────────────────────────────────
RST  = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"

def _c(text, code): return f"\033[{code}m{text}{RST}"

RED    = lambda t: _c(t, 91)
GREEN  = lambda t: _c(t, 92)
YELLOW = lambda t: _c(t, 93)
BLUE   = lambda t: _c(t, 94)
CYAN   = lambda t: _c(t, 96)
WHITE  = lambda t: _c(t, 97)
BOLD_W = lambda t: _c(t, "1;97")
GRAY   = lambda t: _c(t, 90)


# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _rule(char="─", width=70, color=GRAY):
    print(color(char * width))


def _banner():
    print()
    _rule("═")
    print(BOLD_W("  ⛅  OpenWeatherMap Dashboard"))
    _rule("═")
    print()


def _section(title: str):
    print()
    _rule("─", 60, BLUE)
    print(f"  {CYAN(title)}")
    _rule("─", 60, BLUE)


def _kv(key: str, val, unit: str = "", width: int = 26):
    bar = GRAY("│")
    print(f"  {bar}  {WHITE(key.ljust(width))} {YELLOW(str(val))}{GRAY(' '+unit if unit else '')}")


def _weather_bar(value: float, max_val: float, width: int = 30, color=CYAN) -> str:
    filled = int((value / max(max_val, 0.01)) * width)
    return color("█" * filled) + GRAY("░" * (width - filled))


def _wind_direction(deg: float) -> str:
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[int((deg % 360) / 22.5) % 16]


def _beaufort(speed_ms: float) -> str:
    table = [
        (0.5, "Calm "),
        (1.5, "Light air"),
        (3.3, "Light breeze"),
        (5.5, "Gentle breeze"),
        (7.9, "Moderate breeze"),
        (10.7, "Fresh breeze"),
        (13.8, "Strong breeze"),
        (17.1, "Near gale"),
        (20.7, "Gale"),
        (24.4, "Severe gale"),
        (28.4, "Storm"),
        (32.6, "Violent storm"),
        (1e9, "Hurricane"),
    ]
    for limit, label in table:
        if speed_ms < limit:
            return label
    return "Hurricane"


# ─────────────────────────────────────────────────────────────────────────────
# PRINT FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def print_summary(df, city: str, summary: dict):
    _section(f"📍  City: {city}")
    print(f"  {GRAY('│')}  {GRAY('Period:')} "
          f"{df['time'].iloc[0].strftime('%a %d %b %H:%M')} → "
          f"{df['time'].iloc[-1].strftime('%a %d %b %H:%M')}")
    print(f"  {GRAY('│')}  {GRAY('Slots:')} {summary['total_slots']} × 3-hour intervals  "
          f"({summary['days_covered']} days)")
    print()
    _section("📊  Summary Statistics")
    rows_left = [
        ("Avg Temperature",  summary["temp_avg"],      "°C"),
        ("Max Temperature",  summary["temp_max"],      "°C"),
        ("Min Temperature",  summary["temp_min"],      "°C"),
        ("Avg Humidity",     summary["humidity_avg"],  "%"),
    ]
    rows_right = [
        ("Avg Pressure",     summary["pressure_avg"],  "hPa"),
        ("Max Wind Speed",   summary["wind_max"],      "m/s"),
        ("Max Precip. Prob.", summary["pop_max"],      "%"),
        ("Avg Dew Point",    summary["dew_point_avg"], "°C"),
    ]
    for (k1,v1,u1), (k2,v2,u2) in zip(rows_left, rows_right):
        bar = GRAY("│")
        line1 = f"  {bar}  {WHITE(k1.ljust(22))} {YELLOW(str(v1)+' '+u1)}"
        line2 = f"   {bar}  {WHITE(k2.ljust(22))} {YELLOW(str(v2)+' '+u2)}"
        print(line1 + "   " + line2)


def print_forecast_table(df):
    _section("📅  Detailed Forecast (every 3 hours)")
    header = (
        f"  {'Time':<18}  {'Temp':>6}  {'Feels':>6}  "
        f"{'Hum':>5}  {'Wind':>7}  {'Dir':>5}  {'Pop':>5}  {'Cloud':>6}  Description"
    )
    print(GRAY(header))
    _rule("─", 100, GRAY)

    prev_day = None
    for _, row in df.iterrows():
        day = row["day_label"]
        if day != prev_day:
            print(f"\n  {CYAN(BOLD+day)}")
            prev_day = day

        t    = row["time"].strftime("%H:%M")
        temp = f"{row['temp']:+.1f}°C"
        feel = f"{row['feels_like']:+.1f}°C"
        hum  = f"{row['humidity']:.0f}%"
        ws   = f"{row['wind_speed']:.1f}m/s"
        wdir = _wind_direction(row["wind_deg"])
        pop  = f"{row['pop']:.0f}%"
        cld  = f"{row['clouds']:.0f}%"
        desc = row["description"].capitalize()

        # colour temp
        if row["temp"] >= 30:   tc = RED
        elif row["temp"] >= 20: tc = YELLOW
        elif row["temp"] >= 10: tc = GREEN
        else:                   tc = BLUE

        # colour precip
        if row["pop"] >= 60:   pc = RED
        elif row["pop"] >= 30: pc = YELLOW
        else:                  pc = GREEN

        print(
            f"  {GRAY(t):<10}  {tc(temp):>10}  {GRAY(feel):>10}  "
            f"{CYAN(hum):>9}  {YELLOW(ws):>11}  {GRAY(wdir):>5}  "
            f"{pc(pop):>9}  {GRAY(cld):>8}  {WHITE(desc)}"
        )


def print_daily_summary(df):
    _section("📆  Daily Digest")
    daily = df.groupby("day_label").agg(
        temp_min=("temp_min", "min"),
        temp_max=("temp_max", "max"),
        humidity=("humidity", "mean"),
        wind_max=("wind_speed", "max"),
        pop_max=("pop", "max"),
        description=("description", "first"),
    ).reset_index()

    for _, row in daily.iterrows():
        bar_temp = _weather_bar(row["temp_max"] - row["temp_min"],
                                daily["temp_max"].max(), 20)
        bar_pop  = _weather_bar(row["pop_max"], 100, 20, BLUE)
        temp_min = f"{row['temp_min']:.1f}°C"
        temp_max = f"{row['temp_max']:.1f}°C"
        humidity = f"{row['humidity']:.0f}%"
        wind_max = f"{row['wind_max']:.1f} m/s"
        pop_max = f"{row['pop_max']:.0f}%"
        print(f"\n  {CYAN(BOLD + row['day_label'])}")
        print(f"    🌡  {YELLOW(temp_min)} → {RED(temp_max)}  {bar_temp}")
        print(f"    💧  Humidity avg {CYAN(humidity)}   "
              f"🌬 Max wind {YELLOW(wind_max)} "
              f"({GRAY(_beaufort(row['wind_max']))})")
        print(f"    🌧  Precip prob max {bar_pop}  {RED(pop_max)}")
        print(f"    ☁   {GRAY(row['description'].capitalize())}")


def print_alerts(df):
    """Simple rule-based weather alerts."""
    alerts = []
    if df["temp_max"].max() >= 35:
        alerts.append(("🔴 HEAT ALERT", f"Max temp {df['temp_max'].max():.1f}°C ≥ 35°C", RED))
    if df["temp_min"].min() <= 0:
        alerts.append(("🔵 FROST ALERT", f"Min temp {df['temp_min'].min():.1f}°C ≤ 0°C", BLUE))
    if df["wind_speed"].max() >= 14:
        alerts.append(("🟡 WIND ALERT", f"Max wind {df['wind_speed'].max():.1f} m/s — strong gusts likely", YELLOW))
    if df["pop"].max() >= 70:
        alerts.append(("🌧 HEAVY RAIN RISK", f"Precipitation probability peaks at {df['pop'].max():.0f}%", CYAN))

    if alerts:
        _section("⚠   Weather Alerts")
        for title, msg, clr in alerts:
            print(f"  {clr(title)}  {GRAY('—')}  {WHITE(msg)}")
    else:
        _section("✅  No Weather Alerts")
        print(f"  {GREEN('All conditions within normal range.')}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="OpenWeatherMap Dashboard — Task 1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--city", type=str, default=None,
                        help="City name (prompted if omitted)")
    parser.add_argument("--save", type=str, default=None,
                        help="Save dashboard image (e.g. dashboard.png)")
    parser.add_argument("--no-display", action="store_true",
                        help="Skip matplotlib window (useful in CI)")
    args = parser.parse_args()

    _banner()

    # ── city input ────────────────────────────────────────────────────────────
    if args.city:
        city_input = args.city.strip()
    else:
        try:
            city_input = input(f"  {CYAN('Enter city name')}  › ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Aborted.")
            sys.exit(0)

    if not city_input:
        print(RED("  City name cannot be empty. Exiting."))
        sys.exit(1)

    # ── fetch ─────────────────────────────────────────────────────────────────
    print()
    _rule("─", 50, GRAY)
    print(f"  {CYAN('Fetching forecast for')}  {BOLD_W(city_input)} …")
    forecast_data, current_data = fetch_all(city_input)

    if forecast_data is None:
        print(RED("  ✖  Could not retrieve forecast data. Check API key / city name."))
        sys.exit(1)

    # ── extract ───────────────────────────────────────────────────────────────
    df, city = extract_data(forecast_data)
    if df.empty:
        print(RED("  ✖  Extraction returned empty dataset."))
        sys.exit(1)

    summary = compute_summary(df)

    # ── save CSV ──────────────────────────────────────────────────────────────
    csv_path = f"weather_data_{city}.csv"
    df.to_csv(csv_path, index=False)
    print(f"  ✔  CSV saved → {GREEN(csv_path)}")

    # ── terminal output ───────────────────────────────────────────────────────
    print_summary(df, city, summary)
    print_daily_summary(df)
    print_forecast_table(df)
    print_alerts(df)

    # ── dashboard ─────────────────────────────────────────────────────────────
    _section("📈  Generating Dashboard")

    # auto-save path if --save not given
    save_path = args.save or f"dashboard_{city}_{datetime.now().strftime('%Y%m%d_%H%M')}.png"

    if args.no_display:
        print(f"  {GRAY('(--no-display set: saving only, no window)')}")
        dashboard_plot(df, city, summary, save_path=save_path)
    else:
        # Save AND show
        dashboard_plot(df, city, summary, save_path=save_path)

    _rule("═")
    print(BOLD_W("  ✅  All done!"))
    print(f"  {GRAY('CSV:')}      {GREEN(csv_path)}")
    print(f"  {GRAY('Dashboard:')} {GREEN(save_path)}")
    _rule("═")
    print()


if __name__ == "__main__":
    main()