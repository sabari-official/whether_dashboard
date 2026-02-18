# Task - 1: API Integration and Data Visualization

**OpenWeatherMap Dashboard**

---

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

**Project Structure**

```
Task-1/
├── main.py              (297 lines) - CLI orchestrator
├── api.py               (140 lines) - API & fallback handler
├── extract.py           (163 lines) - Data transformation
├── dashboard.py         (341 lines) - Visualization
├── requirements.txt     - Dependencies
└── .env                 - API configuration
```

**Total Code**: 941 lines across 4 Python modules

---

## **CODE MODULES EXPLANATION**

**api.py** - Fetches 5-day forecast (40 entries); handles network timeouts; CSV fallback for offline capability

**extract.py** - JSON to DataFrame conversion; computes heat index (temp≥27°C & humidity≥40%), wind chill (temp≤10°C & wind≥4.8 km/h), dew point; normalizes units (m/s→km/h)

**dashboard.py** - 6 matplotlib subplots: temperature, humidity, pressure, wind, precipitation, cloud coverage; GitHub dark theme with custom colors

**main.py** - CLI with argparse; ANSI color formatting; wind direction & Beaufort scale; formatted terminal output with visual elements

---

## **EXECUTION FLOW**

1. User: `python main.py --city "London"`
2. API fetches data or loads CSV fallback
3. Extract transforms JSON → DataFrame
4. Main displays colored summary
5. Dashboard generates 6-panel visualization

---

## **KEY TECHNICAL FEATURES**

- **Error Resilience**: API failures → CSV fallback
- **Scientific Accuracy**: ISO-compliant meteorological formulas
- **Data Richness**: 18 computed columns from single API call
- **Visual Excellence**: Dark theme with gradient colormaps
- **Professional UI**: Color-coded terminal with ASCII bars

---


## **OUTPUT**
<img width="3202" height="1934" alt="Image" src="https://github.com/user-attachments/assets/2ef457f0-07a3-4481-a710-390f02c8024f" />

---

## **Video**
https://github.com/user-attachments/assets/f1e436c9-80fc-4313-89cd-a02d89d5d023

https://github.com/user-attachments/assets/fe5ab6b5-208e-4102-bce1-01f493f7fb79
---

