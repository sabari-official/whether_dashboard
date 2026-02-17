# OpenWeatherMap Dashboard

---

## **INTERN CREDENTIALS**

**Company**     : CODETECH IT SOLUTIONS
**Name**        : SABARIVASAN E
**Intern ID**   : CTIS3748
**Domain**      : PYTHON PROGRAMMING
**Duration**    : 4 WEEKS
**Mentor**      : NEELA SANTHOSH

---

## **PROJECT OVERVIEW**

The OpenWeatherMap Dashboard is a comprehensive Python application designed to fetch, process, and visualize weather forecast data in an interactive and visually appealing manner. This project demonstrates advanced data manipulation, API integration, and professional data visualization techniques using modern Python libraries. The application provides detailed weather analytics including temperature trends, humidity patterns, pressure variations, wind dynamics, and precipitation probabilities over a 5-day period with 3-hour intervals, serving as a complete solution for weather intelligence and meteorological analysis.

---

## **TASK TYPE PERFORMED**

1. **API Integration** - OpenWeatherMap REST API with CSV fallback mechanism for offline capability
2. **Data Processing** - JSON to pandas DataFrame conversion with unit normalization (m/s→km/h)
3. **Meteorological Calculations** - Heat index (Rothfusz formula), wind chill (Canadian formula), dew point (Magnus approximation)
4. **Dashboard Visualization** - 6-panel matplotlib with dark theme and coordinated layouts
5. **CLI Development** - Command-line interface with color-coded ANSI terminal output

---

## **TOOLS AND RESOURCES USED**

| **Category** | **Tools & Technologies** |
|-------------|--------------------------|
| **Language** | Python 3.9+ |
| **Data Processing** | Pandas (v1.x), NumPy (v1.26.4) |
| **API & Networking** | Requests library, REST API integration |
| **Visualization** | Matplotlib, Seaborn, NumPy |
| **Configuration** | python-dotenv for environment management |
| **Data Formats** | JSON (API), CSV (fallback), DataFrames |
| **Terminal Enhancement** | ANSI Color Codes, Unicode Symbols |
| **Libraries Summary** | requests, pandas, numpy, matplotlib, seaborn, python-dotenv |

---

## **EDITOR USED**

- **Visual Studio Code (VS Code)** - Primary development environment
- **Python Extensions** - Debugging, linting, and execution support

---

## **APPLICABILITY & USE CASES**

1. **Weather Forecasting Applications** - Real-time dashboards for web and mobile platforms
2. **Climate Monitoring Systems** - Agricultural, aviation, maritime weather analysis
3. **Data Visualization Education** - Learning matplotlib and seaborn best practices
4. **API Integration Patterns** - RESTful API consumption and error handling demonstrations
5. **Business Intelligence** - Weather impact analysis for operational and financial planning
6. **Environmental Monitoring** - Long-term climate trend analysis and prediction
7. **Smart City Solutions** - Integration with IoT systems for urban weather management

---

## **COMPLETE PROJECT DETAILS**
PROJECT STRUCTURE**

```
Task-1/
├── main.py              (297 lines) - CLI orchestrator
├── api.py               (140 lines) - API client & fallback handler
├── extract.py           (163 lines) - Data transformation engine
├── dashboard.py         (341 lines) - Visualization generation
├── requirements.txt     - Dependencies
├── .env                 - API key configuration
└── .gitignore          - Git exclusions
```

**Total Production Code**: 941 lines across 4 Python modules

---

## **CODE MODULES EXPLANATION**

**api.py** - Fetches 5-day forecast (40 entries × 3-hour intervals), handles network timeouts, and converts CSV fallback data to OpenWeatherMap JSON format for seamless integration

**extract.py** - Transforms JSON to DataFrame with 18 computed columns; calculates heat index when temp≥27°C & humidity≥40%, wind chill when temp≤10°C & wind≥4.8 km/h, and dew point using Magnus approximation; normalizes units and extracts time labels

**dashboard.py** - Creates 6 subplots: temperature (with min-max shading), humidity (with dew point overlay), pressure (annotated min/max), wind (compass rose + Beaufort scale), precipitation (0-100% PoP), and cloud coverage; implements GitHub dark theme with custom color palette

**main.py** - Argparse for city input; ANSI color formatting; wind direction mapping (0-360° to compass points); Beaufort classification (Calm→Hurricane); formatted terminal output with visual progress bars and styled separators

---


## **EXECUTION FLOW**

1. User inputs city: `python main.py --city "London"`
2. API fetches data (or loads CSV fallback)
3. Extract transforms JSON → enriched DataFrame
4. Main displays colored terminal summary statistics
5. Dashboard generates 6-panel matplotlib visualization
6. Output: Complete 5-day weather intelligence report


## **KEY TECHNICAL FEATURES**

- **Error Resilience**: API failures → automatic CSV fallback with no service interruption
- **Scientific Accuracy**: ISO-compliant meteorological formulas for thermal & wind indices
- **Data Richness**: 18 output columns from single API call (original + computed fields)
- **Visual Excellence**: Dark theme, gradient colormaps, coordinated multi-panel layouts
- **Professional UI**: Color-coded terminal with ASCII bars, Unicode symbols, formatted tables