"""
weather_service.py
------------------
Integrates with the 100% FREE Open-Meteo Weather API (No API Key required).
Calculates real-time environmental hazard multipliers for dynamic auto insurance pricing.
Provides automatic offline fallback if internet access is unavailable.
"""

import urllib.request
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# Preset city coordinates for instant testing
POPULAR_CITIES = {
    "San Francisco, CA": {"lat": 37.7749, "lon": -122.4194},
    "New York, NY": {"lat": 40.7128, "lon": -74.0060},
    "Chicago, IL": {"lat": 41.8781, "lon": -87.6298},
    "Seattle, WA": {"lat": 47.6062, "lon": -122.3321},
    "Austin, TX": {"lat": 30.2672, "lon": -97.7431},
    "London, UK": {"lat": 51.5074, "lon": -0.1278},
    "Tokyo, Japan": {"lat": 35.6762, "lon": 139.6503},
    "Mumbai, India": {"lat": 19.0760, "lon": 72.8777}
}


class WeatherRiskService:
    """
    Evaluates road surface danger and accident probability multipliers
    based on real-time weather conditions.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    def fetch_live_weather(cls, lat: float, lon: float, timeout_sec: int = 4) -> Dict[str, Any]:
        """
        Calls Open-Meteo free API.
        Returns live weather metrics and dynamic insurance road risk factor.
        """
        url = (
            f"{cls.BASE_URL}?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,rain,snowfall,weather_code,wind_speed_10m"
        )

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AntigravityTelematicsInsurance/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    current = data.get("current", {})
                    return cls._parse_weather_and_calculate_risk(current, source="Open-Meteo Live API")
        except Exception as e:
            logger.warning(f"Could not reach live weather API ({e}). Falling back to simulation mode.")

        # Fallback simulation if offline or error
        return cls._simulate_weather_fallback(lat, lon)

    @classmethod
    def _parse_weather_and_calculate_risk(cls, current: Dict[str, Any], source: str) -> Dict[str, Any]:
        temp_c = current.get("temperature_2m", 20.0)
        rain_mm = current.get("rain", 0.0)
        snow_cm = current.get("snowfall", 0.0)
        precip_mm = current.get("precipitation", 0.0)
        wind_kmh = current.get("wind_speed_10m", 12.0)
        wmo_code = current.get("weather_code", 0)

        # Actuarial Road Hazard Multiplier Calculation
        # Baseline = 1.00 (Dry, clear conditions)
        risk_multiplier = 1.00
        hazard_reasons = []

        if snow_cm > 0.5 or (temp_c <= 1.0 and precip_mm > 0.1):
            risk_multiplier += 0.18
            hazard_reasons.append(f"Black ice / Snow risk (Temp: {temp_c}°C, Snow: {snow_cm}cm)")
        elif rain_mm > 5.0:
            risk_multiplier += 0.12
            hazard_reasons.append(f"Heavy rain & hydroplaning risk ({rain_mm} mm/hr)")
        elif rain_mm > 0.5:
            risk_multiplier += 0.06
            hazard_reasons.append(f"Wet pavement / reduced traction ({rain_mm} mm/hr)")

        if wind_kmh > 45.0:
            risk_multiplier += 0.07
            hazard_reasons.append(f"Severe crosswinds ({wind_kmh} km/h)")
        elif wind_kmh > 30.0:
            risk_multiplier += 0.03
            hazard_reasons.append(f"Moderate gusty winds ({wind_kmh} km/h)")

        if not hazard_reasons:
            hazard_reasons.append("Optimal dry road conditions (Low environmental risk)")

        risk_multiplier = round(max(0.95, min(1.25, risk_multiplier)), 3)

        return {
            "source": source,
            "temperature_c": temp_c,
            "rain_mm": rain_mm,
            "snow_cm": snow_cm,
            "wind_speed_kmh": wind_kmh,
            "weather_code": wmo_code,
            "weather_condition": cls._wmo_code_to_desc(wmo_code),
            "weather_risk_multiplier": risk_multiplier,
            "hazard_reasons": hazard_reasons,
            "is_live": True if source.startswith("Open-Meteo") else False
        }

    @classmethod
    def _simulate_weather_fallback(cls, lat: float, lon: float) -> Dict[str, Any]:
        """Provides deterministic, realistic fallback weather based on coordinates."""
        # Simulated mild drizzle or clear weather
        is_wet = abs(int(lat * 10)) % 3 == 0
        temp = 18.5 - abs(lat) * 0.15
        rain = 2.4 if is_wet else 0.0
        wind = 14.0 + (abs(int(lon)) % 10)

        fallback_data = {
            "temperature_2m": round(temp, 1),
            "rain": rain,
            "snowfall": 0.0,
            "precipitation": rain,
            "wind_speed_10m": round(wind, 1),
            "weather_code": 61 if is_wet else 0
        }
        return cls._parse_weather_and_calculate_risk(fallback_data, source="Offline Telematics Weather Simulator")

    @staticmethod
    def _wmo_code_to_desc(code: int) -> str:
        wmo_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            80: "Rain showers",
            95: "Thunderstorm"
        }
        return wmo_map.get(code, "Clear / Normal")
