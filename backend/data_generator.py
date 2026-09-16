"""
data_generator.py
-----------------
Generates realistic telematics trips, second-by-second sensor streams,
and 1,000-driver actuarial fleet dataset for model calibration and demonstration.
"""

import os
import json
import csv
import math
import random
from typing import List, Dict, Any


def ensure_directory(path: str):
    os.makedirs(path, exist_ok=True)


def generate_sample_trip(trip_type: str = "commute") -> Dict[str, Any]:
    """
    Generates an empirical commuter trip along the US-101 South highway corridor
    (San Francisco SOMA -> San Mateo -> Palo Alto) with realistic sensor telemetry.
    """
    # Key landmark waypoints strictly along US-101 South Highway on land
    key_coords = [
        (37.7712, -122.4082),  # SF Downtown / SOMA 101 on-ramp
        (37.7554, -122.4055),  # Potrero Hill
        (37.7390, -122.4042),  # Bernal Heights / Bayshore Blvd
        (37.7198, -122.4018),  # Visitacion Valley
        (37.6975, -122.3985),  # Brisbane
        (37.6625, -122.4055),  # South San Francisco Grand Ave
        (37.6358, -122.4085),  # San Bruno / I-380 Junction
        (37.6158, -122.3925),  # Millbrae
        (37.5985, -122.3725),  # Burlingame
        (37.5785, -122.3485),  # San Mateo North
        (37.5625, -122.3195),  # San Mateo 3rd Ave
        (37.5415, -122.2985),  # Hillsdale / CA-92
        (37.5255, -122.2745),  # Belmont
        (37.5065, -122.2545),  # San Carlos
        (37.4925, -122.2355),  # Redwood City
        (37.4725, -122.2025),  # Menlo Park
        (37.4525, -122.1385)   # Palo Alto University Ave
    ]

    total_steps = 45
    points = []
    events = []
    hard_brakes_count = 0
    rapid_accels_count = 0
    speeding_seconds = 0
    distraction_seconds = 0

    import numpy as np
    lats = [c[0] for c in key_coords]
    lons = [c[1] for c in key_coords]
    orig_idx = np.linspace(0, len(key_coords) - 1, len(key_coords))
    target_idx = np.linspace(0, len(key_coords) - 1, total_steps)
    interp_lats = np.interp(target_idx, orig_idx, lats)
    interp_lons = np.interp(target_idx, orig_idx, lons)

    speed = 52.0  # mph highway cruise

    for i in range(total_steps):
        lat = float(interp_lats[i])
        lon = float(interp_lons[i])

        event_type = "normal"
        g_long = round(random.uniform(-0.06, 0.08), 2)
        g_lat = round(random.uniform(-0.04, 0.04), 2)
        phone_screen_on = False
        speed_limit = 65.0 if (i > 8 and i < 40) else 45.0

        if i == 14:
            # Sudden traffic slowdown deceleration near South SF
            event_type = "hard_braking"
            g_long = -0.46
            speed = 28.0
            hard_brakes_count += 1
            events.append({
                "step": i,
                "type": "Hard Braking Event",
                "severity": "High Severity (-0.46g)",
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "message": "Sudden deceleration logged at 52 mph on US-101 South near South San Francisco."
            })
        elif i == 29:
            # Secondary braking event near Belmont
            event_type = "hard_braking"
            g_long = -0.42
            speed = 34.0
            hard_brakes_count += 1
            events.append({
                "step": i,
                "type": "Hard Braking Event",
                "severity": "Moderate Severity (-0.42g)",
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "message": "Abrupt deceleration event logged near Belmont exit."
            })
        elif i in [22, 23, 24]:
            # Speeding segment past San Mateo
            event_type = "speeding"
            speed = 78.5  # Limit is 65
            speeding_seconds += 10
            if i == 22:
                events.append({
                    "step": i,
                    "type": "Speed Limit Exceedance",
                    "severity": "Warning (+13.5 mph over limit)",
                    "lat": round(lat, 5),
                    "lon": round(lon, 5),
                    "message": "Vehicle sustained 78.5 mph in a 65 mph posted zone on US-101 South."
                })
        elif i in [33, 34, 35]:
            # Phone distraction segment
            event_type = "phone_distraction"
            phone_screen_on = True
            distraction_seconds += 10
            if i == 33:
                events.append({
                    "step": i,
                    "type": "Driver Phone Distraction",
                    "severity": "High Risk (Screen Active)",
                    "lat": round(lat, 5),
                    "lon": round(lon, 5),
                    "message": "Continuous screen active and angular movement logged while cruising at 58 mph."
                })
        else:
            speed = round(min(speed_limit + 3, max(42.0, speed + random.uniform(-1.5, 2.0))), 1)

        points.append({
            "timestamp_sec": i * 10,
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "speed_mph": round(speed, 1),
            "speed_limit_mph": speed_limit,
            "accel_g": g_long,
            "lateral_g": g_lat,
            "phone_screen_on": phone_screen_on,
            "event_type": event_type
        })

    trip_distance_miles = 24.8
    trip_score = max(35, round(100 - (hard_brakes_count * 12 + rapid_accels_count * 6 + (speeding_seconds / 10) * 5 + (distraction_seconds / 10) * 7)))

    return {
        "trip_id": "TRIP-2026-SF-8841",
        "driver_id": "DRV-1092-FLEET",
        "route_name": "US-101 South Corridor: San Francisco to Palo Alto",
        "start_time": "2026-09-10T08:15:00Z",
        "duration_minutes": 28.5,
        "distance_miles": trip_distance_miles,
        "trip_driving_score": trip_score,
        "hard_brakes_count": hard_brakes_count,
        "rapid_accels_count": rapid_accels_count,
        "speeding_duration_sec": speeding_seconds,
        "distraction_duration_sec": distraction_seconds,
        "events": events,
        "telemetry_points": points
    }


def generate_fleet_dataset(num_drivers: int = 1000) -> List[Dict[str, Any]]:
    """
    Generates 1,000 synthetic driver profiles across 5 representative archetypes:
    1. Safe Commuter (35%)
    2. Low-Mileage Weekend Driver (20%)
    3. Night Shift Professional (15%)
    4. Distracted Urbanite (15%)
    5. Aggressive Speedster (15%)
    """
    archetypes = [
        {
            "name": "Safe Commuter",
            "weight": 0.35,
            "braking_range": (0.3, 1.4),
            "accel_range": (0.4, 1.3),
            "speeding_range": (1.0, 4.5),
            "distraction_range": (0.2, 1.8),
            "cornering_range": (0.2, 1.0),
            "night_pct_range": (2.0, 7.0),
            "miles_range": (9000, 14000),
            "age_range": (28, 62),
            "claim_prob": 0.038
        },
        {
            "name": "Low-Mileage Weekend Driver",
            "weight": 0.20,
            "braking_range": (0.8, 2.2),
            "accel_range": (0.6, 1.8),
            "speeding_range": (2.0, 6.0),
            "distraction_range": (0.8, 2.5),
            "cornering_range": (0.5, 1.5),
            "night_pct_range": (3.0, 9.0),
            "miles_range": (3500, 7000),
            "age_range": (32, 68),
            "claim_prob": 0.032
        },
        {
            "name": "Night Shift Worker",
            "weight": 0.15,
            "braking_range": (1.2, 2.8),
            "accel_range": (1.0, 2.2),
            "speeding_range": (4.0, 9.0),
            "distraction_range": (1.5, 3.5),
            "cornering_range": (1.0, 2.2),
            "night_pct_range": (35.0, 65.0),
            "miles_range": (11000, 16000),
            "age_range": (24, 55),
            "claim_prob": 0.075
        },
        {
            "name": "Distracted Urbanite",
            "weight": 0.15,
            "braking_range": (3.5, 6.8),
            "accel_range": (2.5, 4.8),
            "speeding_range": (8.0, 18.0),
            "distraction_range": (7.0, 15.0),
            "cornering_range": (2.5, 5.0),
            "night_pct_range": (8.0, 18.0),
            "miles_range": (10000, 15000),
            "age_range": (21, 38),
            "claim_prob": 0.135
        },
        {
            "name": "Aggressive Speedster",
            "weight": 0.15,
            "braking_range": (4.5, 8.5),
            "accel_range": (4.0, 7.5),
            "speeding_range": (22.0, 45.0),
            "distraction_range": (4.0, 10.0),
            "cornering_range": (3.8, 6.5),
            "night_pct_range": (15.0, 32.0),
            "miles_range": (14000, 22000),
            "age_range": (19, 32),
            "claim_prob": 0.198
        }
    ]

    random.seed(42)
    records = []

    # Import pricing engine to score each driver
    from backend.pricing_engine import DynamicPricingEngine, DriverTelemetryInput
    engine = DynamicPricingEngine()

    for i in range(1, num_drivers + 1):
        arch = random.choices(
            archetypes,
            weights=[a["weight"] for a in archetypes],
            k=1
        )[0]

        age = random.randint(*arch["age_range"])
        miles = round(random.uniform(*arch["miles_range"]), 0)
        braking = round(random.uniform(*arch["braking_range"]), 2)
        accel = round(random.uniform(*arch["accel_range"]), 2)
        speeding = round(random.uniform(*arch["speeding_range"]), 1)
        distraction = round(random.uniform(*arch["distraction_range"]), 1)
        cornering = round(random.uniform(*arch["cornering_range"]), 2)
        night_pct = round(random.uniform(*arch["night_pct_range"]), 1)
        veh_val = round(random.uniform(18000, 48000), 0)

        # Claim generation
        has_claim = 1 if random.random() < arch["claim_prob"] else 0
        claim_amount = round(random.expovariate(1 / 4200.0) + 800.0, 2) if has_claim else 0.0

        t_input = DriverTelemetryInput(
            annual_mileage=miles,
            hard_braking_per_100mi=braking,
            rapid_accel_per_100mi=accel,
            speeding_pct_of_time=speeding,
            phone_distraction_min_per_hr=distraction,
            harsh_cornering_per_100mi=cornering,
            night_driving_pct=night_pct,
            driver_age=age,
            vehicle_value=veh_val
        )

        res = engine.calculate_dynamic_premium(t_input)

        records.append({
            "driver_id": f"DRV-{1000 + i}",
            "archetype": arch["name"],
            "driver_age": age,
            "vehicle_value": veh_val,
            "annual_mileage": miles,
            "hard_braking_per_100mi": braking,
            "rapid_accel_per_100mi": accel,
            "speeding_pct": speeding,
            "phone_distraction_min_hr": distraction,
            "harsh_cornering_per_100mi": cornering,
            "night_driving_pct": night_pct,
            "driving_score": res.driver_score,
            "risk_tier": res.score_tier,
            "traditional_premium": res.traditional_fixed_premium,
            "dynamic_ubi_premium": res.dynamic_ubi_premium,
            "annual_savings": res.annual_savings,
            "discount_pct": res.discount_percentage,
            "has_claim": has_claim,
            "claim_amount": claim_amount
        })

    return records


def generate_and_save_all_sample_documents(target_dir: str):
    """
    Generates all sample documents and saves them to sample_documents/ folder.
    """
    ensure_directory(target_dir)

    # 1. Raw Telematics Trip JSON
    trip_data = generate_sample_trip()
    raw_trip_path = os.path.join(target_dir, "telematics_trip_raw_log.json")
    with open(raw_trip_path, "w", encoding="utf-8") as f:
        json.dump(trip_data, f, indent=2)

    # 2. 1,000 Driver Actuarial Fleet Dataset CSV
    fleet = generate_fleet_dataset(1000)
    fleet_csv_path = os.path.join(target_dir, "driver_fleet_actuarial_dataset.csv")
    if fleet:
        with open(fleet_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fleet[0].keys())
            writer.writeheader()
            writer.writerows(fleet)

    # 3. Aggregated Trip Summary CSV (50 trips)
    trip_summaries = []
    routes = [
        "SF Downtown → San Mateo",
        "Oakland Hills → Berkeley",
        "San Jose Airport → Sunnyvale Tech Center",
        "Marin County → Presidio Expressway",
        "Fremont Blvd → Palo Alto University Ave"
    ]
    for i in range(1, 51):
        dist = round(random.uniform(4.2, 38.5), 1)
        dur = round(dist * random.uniform(1.8, 2.6), 0)
        score = random.randint(45, 98)
        hb = round(random.uniform(0.1, 4.5), 1)
        sp = round(random.uniform(1.0, 22.0), 1)
        trip_summaries.append({
            "trip_id": f"TRIP-SUMM-{2000 + i}",
            "route_name": random.choice(routes),
            "date": f"2026-09-{random.randint(1, 9):02d}",
            "distance_miles": dist,
            "duration_minutes": dur,
            "trip_safety_score": score,
            "hard_brakes": hb,
            "speeding_pct": sp,
            "fuel_efficiency_mpg": round(24.0 + (score / 100.0) * 11.5, 1)
        })

    summary_csv_path = os.path.join(target_dir, "telematics_trips_summary.csv")
    with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=trip_summaries[0].keys())
        writer.writeheader()
        writer.writerows(trip_summaries)

    # 4. Sample Dynamic Policy Schedule JSON
    policy_schedule = {
        "policy_contract_number": "UBI-POL-2026-77894",
        "insured_name": "Elena Rostova",
        "effective_date": "2026-10-01",
        "expiration_date": "2027-10-01",
        "vehicle": {
            "vin": "1HGCR2F83HA129845",
            "year": 2024,
            "make": "Honda",
            "model": "Accord Hybrid Touring",
            "declared_value": 34500.00
        },
        "telematics_integration": {
            "provider": "Zendrive Mobile Telematics SDK v7.4",
            "device_type": "Smartphone Gyroscope / Accelerometer + BLE Beacon",
            "sampling_frequency_hz": 10,
            "data_retention_days": 90,
            "privacy_standard": "ISO-27001 / GDPR Article 9 Compliant"
        },
        "actuarial_premium_structure": {
            "traditional_demographic_premium_annual": 1580.00,
            "current_telematics_score": 93.4,
            "safety_tier": "Elite Safe (Top 15%)",
            "applied_telematics_discount_pct": 31.5,
            "dynamic_annual_premium": 1082.30,
            "monthly_billing_amount": 90.19,
            "annual_policyholder_savings": 497.70
        },
        "coverage_limits": {
            "bodily_injury_liability": "$250,000 / $500,000",
            "property_damage_liability": "$100,000",
            "collision_deductible": "$500",
            "comprehensive_deductible": "$250"
        }
    }
    policy_path = os.path.join(target_dir, "sample_dynamic_policy_schedule.json")
    with open(policy_path, "w", encoding="utf-8") as f:
        json.dump(policy_schedule, f, indent=2)

    return {
        "raw_trip_path": raw_trip_path,
        "fleet_csv_path": fleet_csv_path,
        "summary_csv_path": summary_csv_path,
        "policy_path": policy_path
    }
