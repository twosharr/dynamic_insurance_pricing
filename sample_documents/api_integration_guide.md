# Free API Integration Guide & Developer Reference

## 1. Overview
This project is engineered to be **100% functional out-of-the-box with ZERO paid API keys or subscriptions required**. All real-time environmental risk factors, interactive GIS mapping, and telematics simulations run on high-performance free and open APIs, backed by intelligent offline fallbacks.

---

## 2. Free APIs Used in the Project

### A. Open-Meteo Weather API (Real-Time Road Hazard Index)
- **Website:** [open-meteo.com](https://open-meteo.com/)
- **Pricing:** 100% Free for non-commercial and open use.
- **Authentication:** **None required (No API key needed)**.
- **Rate Limit:** Up to 10,000 requests per day for free tier.
- **Endpoint Used:**
  ```http
  GET https://api.open-meteo.com/v1/forecast?latitude=37.7749&longitude=-122.4194&current=temperature_2m,relative_humidity_2m,precipitation,rain,snowfall,weather_code,wind_speed_10m
  ```

#### How It Works in This Project:
1. When a user selects a city or enters GPS coordinates in the Dashboard, `backend/weather_service.py` queries the Open-Meteo API.
2. The response provides instantaneous precipitation, snowfall, ambient temperature, and WMO weather codes.
3. The engine computes the **Road Surface Hazard Multiplier**:
   - Dry road: `1.00x`
   - Moderate rain: `1.06x`
   - Heavy rain / hydroplaning: `1.12x`
   - Snow / Black ice: `1.18x - 1.25x`
4. If the server is offline or internet connectivity is unavailable, the system automatically engages the built-in **Offline Telematics Weather Simulator** without throwing errors.

#### Quick cURL Test:
```bash
curl "https://api.open-meteo.com/v1/forecast?latitude=37.7749&longitude=-122.4194&current=temperature_2m,rain,snowfall,wind_speed_10m"
```

---

### B. Leaflet.js & OpenStreetMap (Interactive GIS Route Mapping)
- **Website:** [leafletjs.com](https://leafletjs.com/) & [openstreetmap.org](https://www.openstreetmap.org/)
- **Pricing:** 100% Free & Open Source.
- **Authentication:** **No API key needed**.
- **Tile Server:** OpenStreetMap standard tile layers (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`).
- **Usage:**
  - Renders the interactive route map for the driver's trip.
  - Plots color-coded event markers:
    - 🟢 Green: Smooth cruising
    - 🟡 Yellow: Minor acceleration or speed advisory
    - 🔴 Red: Hard deceleration event (-0.48g) or phone screen interaction
  - Provides a live playback simulation cursor showing vehicle velocity and g-force.

---

### C. Nominatim Geocoding (Optional Free Geolocation)
- **Website:** [nominatim.org](https://nominatim.org/)
- **Pricing:** Free under Open Database License (ODbL).
- **Authentication:** None required (Must provide descriptive `User-Agent`).
- **Endpoint:**
  ```http
  GET https://nominatim.openstreetmap.org/reverse?format=json&lat=37.7749&lon=-122.4194
  ```

---

## 3. Optional Enterprise APIs (How to Upgrade in Production)

If an enterprise carrier or insurer wishes to connect proprietary commercial SDKs, the codebase is designed with modular adapters:

### 1. Zendrive Mobile Telematics SDK
- **Provider:** [zendrive.com](https://www.zendrive.com/)
- **Purpose:** Production mobile smartphone background telematics sensing, automatic collision detection, and trip classification (driver vs. passenger).
- **How to configure:**
  1. Obtain an SDK App Key from the Zendrive Developer Portal.
  2. Set environment variable: `ZENDRIVE_SDK_KEY="your_api_key_here"`.
  3. The `backend/pricing_engine.py` directly ingests standard Zendrive trip payload JSON objects.

### 2. Google Maps Platform (Alternative to Leaflet)
- **Purpose:** Satellite imagery, street view, and historical traffic congestion overlays.
- **How to configure:**
  1. Generate an API Key at [console.cloud.google.com](https://console.cloud.google.com/).
  2. Add `GOOGLE_MAPS_API_KEY` to your `.env` file.
  3. Replace the Leaflet tile layer in `frontend/index.html` with Google Maps JavaScript API script tag.

### 3. TomTom Traffic & Hazards API
- **Purpose:** Real-time road construction, lane closures, and accident hazard cones.
- **How to configure:**
  1. Sign up at [developer.tomtom.com](https://developer.tomtom.com/).
  2. Set `TOMTOM_API_KEY` in environment.

---

## 4. Local Verification Commands

To verify API connectivity from your PowerShell terminal:

```powershell
# Test Open-Meteo Weather API integration:
py -c "from backend.weather_service import WeatherRiskService; print(WeatherRiskService.fetch_live_weather(37.7749, -122.4194))"

# Test Dynamic Pricing calculation API:
py -c "from backend.pricing_engine import DynamicPricingEngine, DriverTelemetryInput; e = DynamicPricingEngine(); print(e.calculate_dynamic_premium(DriverTelemetryInput()))"
```
