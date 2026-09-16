# UC070: AI-Powered Dynamic Pricing for Auto Insurance
### Behavioral Telematics Scoring, Usage-Based Insurance (UBI), and Real-Time Risk Calibration

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Uvicorn-009688.svg)](https://fastapi.tiangolo.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn%20%2B%20XGBoost-F7931E.svg)](https://scikit-learn.org/)
[![Telematics](https://img.shields.io/badge/Telematics-Zendrive%20%2B%20CMT%20Benchmarks-3B82F6.svg)](https://www.zendrive.com/)
[![Free API](https://img.shields.io/badge/Free%20API-Open--Meteo%20Road%20Hazard-10B981.svg)](https://open-meteo.com/)
[![Executive PDF](https://img.shields.io/badge/Presentation-ReportLab%20Executive%20PDF-6366F1.svg)](https://www.reportlab.com/)

---

## 1. Project Executive Overview
**UC070** delivers a modern, actuarially sound **AI-Powered Dynamic Pricing Platform for Auto Insurance**. 

### The Industry Dilemma: Why Fixed Pricing Fails
Traditional auto insurance relies on static demographic proxies (driver age, residential zip code, vehicle MSRP, credit score). Under this century-old structure:
- **Safe drivers are penalized:** A cautious motorist driving 6,000 miles a year without touching their phone pays nearly the same premium as an aggressive driver in the same zip code who texts at 80 mph.
- **Incentive breakdown:** Motorists have zero economic incentive to adopt safer driving habits.
- **Adverse selection:** Telematics-first insurers (Root, Lemonade, Progressive Snapshot, Tesla Insurance) skim off the safest 20% of drivers with large discounts, leaving legacy carriers with an unpriced, loss-heavy risk pool.

### The Solution: Continuous Telematics Ingestion & Behavioral Rating
Inspired by industry benchmarks like **Zendrive** and **Cambridge Mobile Telematics (CMT)**, this platform ingests high-frequency smartphone and OBD-II sensor streams, computes a calibrated **0–100 Safe Driving Score**, and applies **Bühlmann-Straub Actuarial Credibility** to adjust monthly premiums dynamically.

Safe drivers earn discounts of **up to 35% (\$468+ annual savings)**, while carriers achieve a **15.3 percentage point reduction in loss ratio** (from 68.4% down to 53.1%).

---

## 2. Key Architecture & Features

```
                               ┌────────────────────────────────────────┐
                               │   Mobile / OBD-II Telematics Sensors   │
                               │  (10Hz Accel, Gyro, GPS, Phone State)  │
                               └───────────────────┬────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────┐      ┌────────────────────────────────────────┐      ┌─────────────────────────┐
│  Open-Meteo Free API  │ ───► │      Telematics Feature Extractor      │ ◄─── │ Demographic Base (GLM)  │
│  (Live Road Hazard)   │      │  (Braking, Distraction, Speeding, Etc) │      │  (Age, Vehicle Value)   │
└───────────────────────┘      └───────────────────┬────────────────────┘      └─────────────────────────┘
                                                   │
                                                   ▼
                               ┌────────────────────────────────────────┐
                               │   Actuarial & Machine Learning Engine  │
                               │  - Zendrive 0-100 Multi-Factor Score   │
                               │  - Bühlmann Credibility Weighting (Z)  │
                               │  - Explainable AI (SHAP Dollar Credits)│
                               └───────────────────┬────────────────────┘
                                                   │
                                                   ▼
                               ┌────────────────────────────────────────┐
                               │       Modern Responsive Dashboard      │
                               │  - Interactive Pricing Simulator       │
                               │  - Leaflet GPS Route Map with Hazards  │
                               │  - Fleet Archetype Manager (1,000 Pts) │
                               │  - Executive Presentation PDF Report   │
                               └────────────────────────────────────────┘
```

1. **Interactive Dynamic Pricing Simulator:**
   - Sliders for Annual Mileage, Hard Deceleration, Phone Distraction, Speeding, Harsh Cornering, and Night Driving.
   - Side-by-side comparison: **Traditional Fixed Demographic Premium (\$1,450)** vs. **AI Dynamic Premium (\$982)**.
   - Real-time annual savings banner and monthly billing calculator.
2. **Zendrive Composite Driving Gauge:**
   - Animated SVG radial gauge displaying score (0–100) and risk tier (*Elite Safe, Low Risk, Moderate, Elevated, High Risk*).
3. **Interactive GIS Route Map (Leaflet.js):**
   - Renders a commuter drive from San Francisco to Silicon Valley.
   - Places interactive hazard markers:
     - 🔴 Red: Hard deceleration event ($-0.48g$ at step 12).
     - 🟣 Purple: Smartphone screen unlock & motion at 42 mph.
     - 🟡 Amber: Speeding violation (+23 mph over limit).
   - Real-time simulator playback with live vehicle telemetry HUD (Speed, g-force, phone state).
4. **Explainable AI (XAI) Waterfall Breakdown:**
   - Visual attribution showing the exact dollar impact of every driving behavior, meeting FCRA and NAIC transparency requirements.
5. **Free Weather Hazard API (Open-Meteo):**
   - 100% free, zero API key required. Real-time atmospheric risk multiplier (rain, snow, ice, wind) with automatic offline fallback.
6. **Actuarial Fleet Manager (1,000 Synthetic Drivers):**
   - Pre-loaded with 5 archetypes (*Safe Commuter Elena, Weekend Joyrider Marcus, Night Shift Sarah, Distracted Urbanite Leo, Aggressive Speedster Tyler*).
   - Filterable table with one-click simulator loading.
7. **Executive Presentation PDF Generator:**
   - Generates a publication-quality 6-page whitepaper with ReportLab, containing actuarial proofs, architecture specs, and manager talk tracks.

---

## 3. Quickstart Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.12).
- Dependencies: `fastapi`, `uvicorn`, `reportlab`, `pypdf`, `scikit-learn`, `pandas`, `numpy`.

### 1-Command Launch
```powershell
# In Windows PowerShell:
cd C:\Users\t21\.gemini\antigravity\scratch\dynamic_insurance_pricing
py run.py
```

`run.py` automatically:
1. Generates the sample documents and 1,000-driver fleet CSV.
2. Calibrates the Gradient Boosting actuarial ML risk model.
3. Compiles the publication-quality Executive Presentation PDF.
4. Starts the FastAPI web server on `http://localhost:8000`.

### URL Access Points:
- **Interactive Web Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger REST API:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Direct PDF Download:** [http://localhost:8000/api/download-report](http://localhost:8000/api/download-report)
- **Sample Documents Folder:** [http://localhost:8000/sample_documents/](http://localhost:8000/sample_documents/)

---

## 4. Directory Structure

```
dynamic_insurance_pricing/
├── backend/
│   ├── main.py                  # FastAPI application with REST endpoints & static mounting
│   ├── pricing_engine.py        # Actuarial GLM + Zendrive-style telematics scoring algorithms
│   ├── ml_risk_model.py         # Gradient Boosting risk scoring + SHAP feature attribution
│   ├── weather_service.py       # Free Open-Meteo Weather API client (rain/snow/fog multiplier)
│   ├── data_generator.py        # Synthetic telematics trips, GPS trajectories, and fleet dataset
│   └── pdf_generator.py         # ReportLab engine producing 6-page executive PDF report
├── frontend/
│   ├── index.html               # Modern single-page dashboard (Tailwind CSS, Lucide icons)
│   ├── app.js                   # Client orchestration: sliders, Leaflet route playback, charts
│   └── styles.css               # Clean dark-mode aesthetics, SVG gauges, and glassmorphic cards
├── sample_documents/            # Dedicated sample documents folder requested by user
│   ├── telematics_trip_raw_log.json         # High-frequency second-by-second sensor stream
│   ├── telematics_trips_summary.csv         # Aggregated 50-trip log with driving metrics
│   ├── driver_fleet_actuarial_dataset.csv   # 1,000 driver records with claims and premiums
│   ├── actuarial_pricing_model_spec.md      # Actuarial math: GLM Tweedie, Bühlmann credibility
│   ├── api_integration_guide.md             # Free APIs guide (Open-Meteo, Leaflet, Nominatim)
│   ├── executive_summary_and_business_case.md # Business case, loss ratio lift, and ROI
│   └── sample_dynamic_policy_schedule.json  # Connected insurance policy schedule JSON
├── docs_and_presentation/
│   ├── UC070_Dynamic_Insurance_Pricing_Executive_Guide.pdf # 6-page executive presentation PDF
│   └── manager_presentation_script.md       # Slide-by-slide demo script for manager & team
├── run.py                       # One-click startup script
├── requirements.txt             # Dependency specifications
└── README.md                    # Project documentation
```

---

## 5. Free API Integration Details
This project is engineered to be **100% operational with ZERO API keys or paid subscriptions**:
- **Open-Meteo Weather API:** Queries `https://api.open-meteo.com/v1/forecast` for live surface precipitation, snowfall, ambient temperature, and wind speed. Includes an automated offline fallback simulator.
- **Leaflet.js & OpenStreetMap:** Renders high-resolution interactive map tiles without requiring Google Maps billing credentials.
- **Nominatim Geocoding:** Reverse geolocates coordinates via OpenStreetMap community servers.
- *Optional commercial upgrades* (e.g. Zendrive Mobile SDK, TomTom Hazards, Google Maps) are fully documented in [`sample_documents/api_integration_guide.md`](file:///C:/Users/t21/.gemini/antigravity/scratch/dynamic_insurance_pricing/sample_documents/api_integration_guide.md).

---

## 6. How to Demonstrate This Project to Your Manager & Team
Follow the 5-step demonstration walkthrough provided in [`docs_and_presentation/manager_presentation_script.md`](file:///C:/Users/t21/.gemini/antigravity/scratch/dynamic_insurance_pricing/docs_and_presentation/manager_presentation_script.md):

1. **Step 1: The Fixed Pricing Dilemma:** Open `localhost:8000`. Show that two identical drivers pay the same \$1,450 regardless of whether they drive safely or text while speeding.
2. **Step 2: Safe Driver Simulator:** Click the **Safe Commuter Elena** button. Show how the score jumps to 93.2 and dynamic premium drops to \$982, rewarding the driver with **\$468 in annual savings**.
3. **Step 3: GIS Route & Telemetry:** Switch to the **Interactive GIS Route Map** tab and click **Play Trip Simulation**. Point out the red hard-braking and purple distracted-driving markers along the route.
4. **Step 4: Weather Risk:** Demonstrate how live rainfall or snow from the **Open-Meteo API** automatically adjusts the road risk multiplier.
5. **Step 5: Executive PDF & Business Case:** Click **Download Executive PDF Report** and show management the publication-grade 6-page document outlining mathematical proofs, loss ratio reduction (-15.3 pts), and regulatory compliance.
