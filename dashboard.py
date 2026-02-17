import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import warnings
from typing import Optional, Dict

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────────────────────
BG        = "#0D1117"   # page background
PANEL_BG  = "#161B22"   # subplot background
GRID_CLR  = "#21262D"   # grid lines
TEXT_CLR  = "#E6EDF3"   # primary text
MUTED     = "#8B949E"   # secondary text

BLUE  = "#58A6FF"
GREEN = "#3FB950"
PURP  = "#BC8CFF"
AMBER = "#D29922"
CORAL = "#F78166"
TEAL  = "#39D0C3"
PINK  = "#FF7EB3"
GOLD  = "#E3B341"

PALETTE = [BLUE, GREEN, PURP, AMBER, CORAL, TEAL, PINK, GOLD]

TEMP_CMAP = LinearSegmentedColormap.from_list(
    "temp",
    ["#1A56DB", "#93C5FD", "#FCD34D", "#F97316", "#DC2626"],
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _style_ax(ax, title: str, ylabel: str = "", xlabel: bool = True):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    ax.set_title(title, color=TEXT_CLR, fontsize=9.5, fontweight="bold", pad=8)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    ax.grid(color=GRID_CLR, linewidth=0.6, linestyle="--", alpha=0.8)
    if xlabel:
        ax.tick_params(axis="x", rotation=30)
        ax.xaxis.label.set_color(MUTED)


def _x_ticks(ax, df, step: int = 4):
    ticks = df.index[::step]
    labels = df["datetime_str"].iloc[::step]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=7, color=MUTED)


# ─────────────────────────────────────────────────────────────────────────────
# INDIVIDUAL PANELS
# ─────────────────────────────────────────────────────────────────────────────
def _temperature_panel(ax, df):
    x = df.index
    ax.fill_between(x, df["temp_min"], df["temp_max"],
                    alpha=0.18, color=BLUE, label="Min–Max range")
    ax.plot(x, df["temp"], color=BLUE, lw=2, label="Temperature (°C)", zorder=5)
    ax.scatter(x, df["temp"], c=df["temp"], cmap=TEMP_CMAP,
               s=25, zorder=6, edgecolors="none")
    ax.plot(x, df["feels_like"], color=CORAL, lw=1.2,
            linestyle="--", label="Feels like", alpha=0.85)
    _style_ax(ax, "🌡  Temperature", "°C")
    _x_ticks(ax, df)
    ax.legend(fontsize=7, framealpha=0, labelcolor=TEXT_CLR)


def _humidity_panel(ax, df):
    x = df.index
    ax.fill_between(x, df["humidity"], alpha=0.25, color=GREEN)
    ax.plot(x, df["humidity"], color=GREEN, lw=2, label="Humidity (%)", zorder=5)
    ax.plot(x, df["dew_point"], color=TEAL, lw=1.2, linestyle="--",
            label="Dew point (°C)", alpha=0.85)
    _style_ax(ax, "💧  Humidity & Dew Point", "%")
    _x_ticks(ax, df)
    ax.legend(fontsize=7, framealpha=0, labelcolor=TEXT_CLR)


def _pressure_panel(ax, df):
    x = df.index
    y = df["pressure"]
    ax.fill_between(x, y, y.min() - 2, alpha=0.2, color=PURP)
    ax.plot(x, y, color=PURP, lw=2, label="Pressure (hPa)", zorder=5)
    # annotate min / max
    idx_max = y.idxmax(); idx_min = y.idxmin()
    for idx, lbl, va in [(idx_max, f"▲{y[idx_max]:.0f}", "bottom"),
                          (idx_min, f"▼{y[idx_min]:.0f}", "top")]:
        ax.annotate(lbl, xy=(idx, y[idx]), fontsize=7.5,
                    color=TEXT_CLR, va=va, ha="center",
                    xytext=(0, 8 if va == "bottom" else -8),
                    textcoords="offset points")
    _style_ax(ax, "🌀  Atmospheric Pressure", "hPa")
    _x_ticks(ax, df)
    ax.legend(fontsize=7, framealpha=0, labelcolor=TEXT_CLR)


def _wind_panel(ax, df):
    x = df.index
    ax.fill_between(x, df["wind_speed"], alpha=0.2, color=AMBER)
    ax.plot(x, df["wind_speed"], color=AMBER, lw=2, label="Wind speed (m/s)")
    # Beaufort colour band
    beaufort_colors = {1.5: "#2ECC71", 5.5: "#F39C12", 11: "#E74C3C"}
    prev = 0
    labels_done = set()
    for threshold, col in beaufort_colors.items():
        label = "Breeze" if threshold == 1.5 else ("Moderate" if threshold == 5.5 else "Strong")
        if label not in labels_done:
            ax.axhspan(prev, threshold, alpha=0.06, color=col, label=label)
            labels_done.add(label)
        prev = threshold
    _style_ax(ax, "🌬  Wind Speed", "m/s")
    _x_ticks(ax, df)
    ax.legend(fontsize=7, framealpha=0, labelcolor=TEXT_CLR, ncol=2)


def _precipitation_panel(ax, df):
    x = df.index
    colors = [TEAL if v < 30 else BLUE if v < 60 else CORAL for v in df["pop"]]
    bars = ax.bar(x, df["pop"], color=colors, width=0.7, alpha=0.85)
    ax.axhline(30, color=MUTED, lw=0.8, linestyle=":", alpha=0.6)
    ax.axhline(60, color=CORAL, lw=0.8, linestyle=":", alpha=0.6)
    ax.set_ylim(0, 105)
    _style_ax(ax, "🌧  Precipitation Probability", "%")
    _x_ticks(ax, df)
    legend_items = [
        mpatches.Patch(color=TEAL,  label="Low (<30%)"),
        mpatches.Patch(color=BLUE,  label="Moderate (30–60%)"),
        mpatches.Patch(color=CORAL, label="High (>60%)"),
    ]
    ax.legend(handles=legend_items, fontsize=7, framealpha=0, labelcolor=TEXT_CLR)


def _cloud_panel(ax, df):
    x = df.index
    ax.fill_between(x, df["clouds"], alpha=0.3, color=MUTED)
    ax.plot(x, df["clouds"], color=TEXT_CLR, lw=1.5, label="Cloud cover (%)")
    # overlay visibility on twin
    ax2 = ax.twinx()
    ax2.plot(x, df["visibility"], color=GOLD, lw=1.2, linestyle="--",
             label="Visibility (km)", alpha=0.85)
    ax2.set_ylabel("Visibility (km)", color=GOLD, fontsize=8)
    ax2.tick_params(colors=GOLD, labelsize=7.5)
    ax2.set_facecolor(PANEL_BG)
    for spine in ax2.spines.values():
        spine.set_edgecolor(GRID_CLR)
    _style_ax(ax, "☁  Cloud Cover & Visibility", "%")
    _x_ticks(ax, df)
    # combined legend
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2,
              fontsize=7, framealpha=0, labelcolor=TEXT_CLR)


def _wind_rose(ax, df):
    dirs = df["wind_deg"].values
    speeds = df["wind_speed"].values
    bins = 16
    step = 360 / bins
    angles = np.deg2rad(np.arange(0, 360, step))

    radii = []
    for i, a in enumerate(np.arange(0, 360, step)):
        mask = (dirs >= a) & (dirs < a + step)
        if mask.any():
            radii.append(speeds[mask].mean())
        else:
            radii.append(0.0)
    radii = np.array(radii)
    width = np.deg2rad(step) * 0.9

    cmap = plt.get_cmap("plasma")
    norm = plt.Normalize(radii.min(), max(radii.max(), 0.01))
    bars = ax.bar(angles, radii, width=width, bottom=0,
                  color=cmap(norm(radii)), alpha=0.85, edgecolor=BG, lw=0.5)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=MUTED, labelsize=7)
    ax.set_title("🧭  Wind Rose", color=TEXT_CLR, fontsize=9.5,
                 fontweight="bold", pad=12)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    ax.yaxis.label.set_color(MUTED)
    ax.grid(color=GRID_CLR, linewidth=0.5, linestyle="--", alpha=0.6)
    # cardinal labels
    cardinals = ["N","NE","E","SE","S","SW","W","NW"]
    ax.set_xticks(np.radians([0, 45, 90, 135, 180, 225, 270, 315]))
    ax.set_xticklabels(cardinals, fontsize=7.5, color=TEXT_CLR)


def _heatmap_panel(ax, df):
    cols = ["temp", "humidity", "pressure", "wind_speed", "pop",
            "dew_point", "clouds"]
    corr = df[cols].corr()
    custom_cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap=custom_cmap,
        linewidths=0.5, linecolor=BG,
        annot_kws={"size": 7, "color": TEXT_CLR},
        ax=ax, vmin=-1, vmax=1,
    )
    ax.set_facecolor(PANEL_BG)
    ax.set_title("📊  Correlation Heatmap", color=TEXT_CLR,
                 fontsize=9.5, fontweight="bold", pad=8)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY HEADER
# ─────────────────────────────────────────────────────────────────────────────
def _draw_summary_bar(fig, df, city: str, summary: Dict):
    
    stats = [
        ("🌡", f"{summary.get('temp_avg','—')} °C", "Avg Temp"),
        ("⬆", f"{summary.get('temp_max','—')} °C", "Max Temp"),
        ("⬇", f"{summary.get('temp_min','—')} °C", "Min Temp"),
        ("💧", f"{summary.get('humidity_avg','—')} %", "Avg Humidity"),
        ("🌀", f"{summary.get('pressure_avg','—')} hPa", "Avg Pressure"),
        ("🌬", f"{summary.get('wind_max','—')} m/s", "Max Wind"),
        ("🌧", f"{summary.get('pop_max','—')} %", "Max Precip"),
        ("💦", f"{summary.get('dew_point_avg','—')} °C", "Dew Point"),
    ]
    n = len(stats)
    w = 1.0 / n
    for i, (icon, value, label) in enumerate(stats):
        x = i * w + w / 2
        fig.text(x, 0.965, icon, ha="center", va="center",
                 fontsize=14, color=PALETTE[i % len(PALETTE)])
        fig.text(x, 0.948, value, ha="center", va="center",
                 fontsize=9.5, fontweight="bold", color=TEXT_CLR)
        fig.text(x, 0.933, label, ha="center", va="center",
                 fontsize=7, color=MUTED)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def dashboard_plot(df, city: str, summary: Optional[Dict] = None, save_path: Optional[str] = None):
    
    if df.empty:
        print("  ✖  No data to plot.")
        return

    from extract import compute_summary
    if summary is None:
        summary = compute_summary(df)

    matplotlib.rcParams.update({
        "figure.facecolor": BG,
        "text.color": TEXT_CLR,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.family": "DejaVu Sans",
    })

    fig = plt.figure(figsize=(22, 13), facecolor=BG)

    # ── title ─────────────────────────────────────────────────────────────────
    date_range = (
        f"{df['time'].iloc[0].strftime('%d %b')} – "
        f"{df['time'].iloc[-1].strftime('%d %b %Y')}"
    )
    fig.text(
        0.5, 0.985, f"⛅  Weather Dashboard  ·  {city}",
        ha="center", va="top", fontsize=17, fontweight="bold", color=TEXT_CLR,
    )
    fig.text(
        0.5, 0.972, date_range,
        ha="center", va="top", fontsize=9, color=MUTED,
    )

    _draw_summary_bar(fig, df, city, summary)

    # ── grid 3 × 3 ────────────────────────────────────────────────────────────
    outer = gridspec.GridSpec(
        3, 3,
        figure=fig,
        top=0.91, bottom=0.07,
        left=0.05, right=0.97,
        hspace=0.55, wspace=0.33,
    )

    panels = [
        (0, 0, False),  # temperature  → normal ax
        (0, 1, False),  # humidity
        (0, 2, False),  # pressure
        (1, 0, False),  # wind
        (1, 1, False),  # precipitation
        (1, 2, False),  # cloud cover
        (2, 0, True),   # wind rose    → polar
        (2, 1, False),  # correlation heatmap (spans 2 cols handled below)
        (2, 2, False),
    ]

    ax_temp  = fig.add_subplot(outer[0, 0]); _temperature_panel(ax_temp, df)
    ax_hum   = fig.add_subplot(outer[0, 1]); _humidity_panel(ax_hum, df)
    ax_pres  = fig.add_subplot(outer[0, 2]); _pressure_panel(ax_pres, df)
    ax_wind  = fig.add_subplot(outer[1, 0]); _wind_panel(ax_wind, df)
    ax_pop   = fig.add_subplot(outer[1, 1]); _precipitation_panel(ax_pop, df)
    ax_cloud = fig.add_subplot(outer[1, 2]); _cloud_panel(ax_cloud, df)
    ax_rose  = fig.add_subplot(outer[2, 0], polar=True); _wind_rose(ax_rose, df)
    # heatmap spans 2 columns
    ax_heat  = fig.add_subplot(outer[2, 1:]); _heatmap_panel(ax_heat, df)

    # footer
    from datetime import datetime
    fig.text(
        0.5, 0.01,
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  "
        f"Data: OpenWeatherMap  ·  {summary.get('total_slots','?')} forecast slots",
        ha="center", fontsize=7, color=MUTED,
    )

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=BG)
        print(f"  ✔  Dashboard saved → {save_path}")
    else:
        plt.tight_layout(rect=[0, 0.02, 1, 0.92])
        plt.show()

    plt.close(fig)
