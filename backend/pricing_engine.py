"""
pricing_engine.py
-----------------
Actuarial GLM base rating, Zendrive-inspired telematics driving score calculation,
credibility-weighted dynamic pricing multipliers, and explainability breakdown.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import math


@dataclass
class DriverTelemetryInput:
    annual_mileage: float = 12000.0          # Miles driven per year
    hard_braking_per_100mi: float = 2.5      # Sudden deceleration (> -0.4g / -3.92 m/s²)
    rapid_accel_per_100mi: float = 2.0       # Harsh acceleration (> +0.35g / +3.43 m/s²)
    speeding_pct_of_time: float = 8.0        # % of driving time spent > 10 mph over speed limit
    phone_distraction_min_per_hr: float = 4.0 # Phone screen-on / interaction minutes per hour
    harsh_cornering_per_100mi: float = 1.5   # Lateral acceleration > 0.4g
    night_driving_pct: float = 10.0          # % of miles between 12:00 AM - 4:00 AM
    driver_age: int = 35                     # Demographic base
    vehicle_value: float = 28000.0           # Vehicle base price
    base_location_risk: float = 1.0          # 0.8 (rural) to 1.3 (dense urban)


@dataclass
class PricingBreakdown:
    driver_score: float                      # 0 - 100 Zendrive-style composite score
    score_tier: str                          # Elite Safe, Low Risk, Moderate Risk, Elevated Risk, High Risk
    traditional_fixed_premium: float         # Conventional annual premium based on demographics
    dynamic_ubi_premium: float               # Telematics-adjusted annual dynamic premium
    monthly_dynamic_premium: float           # Monthly billable rate
    annual_savings: float                    # Positive for savings, negative for surcharge
    discount_percentage: float               # Positive for discount, negative for surcharge
    credibility_factor: float                # Bühlmann-Straub credibility Z (0.0 to 1.0)
    sub_scores: Dict[str, float]             # Component sub-scores (0-100 each)
    waterfall_breakdown: List[Dict[str, Any]] # Explainable AI dollar credits/debits
    fairness_metrics: Dict[str, Any]         # Fairness comparison metrics


class DynamicPricingEngine:
    """
    Actuarial & Machine Learning hybrid engine for Usage-Based Insurance (UBI).
    Combines Pay-As-You-Drive (PAYD) and Pay-How-You-Drive (PHYD).
    """

    # Industry benchmarks (Zendrive / CMT / Root calibrated benchmarks)
    BENCHMARKS = {
        "hard_braking_good": 1.0,     # <= 1.0 per 100 miles is good
        "hard_braking_poor": 6.0,     # >= 6.0 per 100 miles is critical risk
        "rapid_accel_good": 1.0,
        "rapid_accel_poor": 5.0,
        "speeding_good": 3.0,         # <= 3% of time
        "speeding_poor": 25.0,        # >= 25% of time
        "distraction_good": 1.0,      # <= 1 min/hr
        "distraction_poor": 12.0,     # >= 12 min/hr
        "cornering_good": 0.8,
        "cornering_poor": 5.0,
        "night_good": 4.0,            # <= 4%
        "night_poor": 25.0,           # >= 25%
        "standard_annual_miles": 13500.0
    }

    # Actuarial weights for composite driving score (Sum to 1.0)
    SCORE_WEIGHTS = {
        "hard_braking": 0.25,        # 25% - High predictive power for rear-end collisions
        "phone_distraction": 0.25,   # 25% - Leading cause of severe modern accidents
        "speeding": 0.20,            # 20% - Amplifies collision severity
        "harsh_cornering": 0.10,     # 10% - Lateral instability & lane drift
        "rapid_accel": 0.10,         # 10% - Aggression proxy
        "night_driving": 0.10        # 10% - Fatigue and low visibility risk
    }

    @staticmethod
    def _normalize_metric(value: float, good_thresh: float, poor_thresh: float) -> float:
        """
        Converts raw telematics value into a 0 - 100 safety score.
        Lower raw values yield higher scores (safer).
        """
        if value <= good_thresh:
            return 100.0
        if value >= poor_thresh:
            return 20.0
        ratio = (value - good_thresh) / (poor_thresh - good_thresh)
        return max(0.0, min(100.0, 100.0 - (ratio * 80.0)))

    def calculate_telematics_score(self, telemetry: DriverTelemetryInput) -> Dict[str, Any]:
        """Calculates component sub-scores and weighted Zendrive-style composite score."""
        b = self.BENCHMARKS

        sub_scores = {
            "braking_score": self._normalize_metric(telemetry.hard_braking_per_100mi, b["hard_braking_good"], b["hard_braking_poor"]),
            "distraction_score": self._normalize_metric(telemetry.phone_distraction_min_per_hr, b["distraction_good"], b["distraction_poor"]),
            "speeding_score": self._normalize_metric(telemetry.speeding_pct_of_time, b["speeding_good"], b["speeding_poor"]),
            "cornering_score": self._normalize_metric(telemetry.harsh_cornering_per_100mi, b["cornering_good"], b["cornering_poor"]),
            "accel_score": self._normalize_metric(telemetry.rapid_accel_per_100mi, b["rapid_accel_good"], b["rapid_accel_poor"]),
            "night_score": self._normalize_metric(telemetry.night_driving_pct, b["night_good"], b["night_poor"]),
        }

        composite_score = (
            sub_scores["braking_score"] * self.SCORE_WEIGHTS["hard_braking"] +
            sub_scores["distraction_score"] * self.SCORE_WEIGHTS["phone_distraction"] +
            sub_scores["speeding_score"] * self.SCORE_WEIGHTS["speeding"] +
            sub_scores["cornering_score"] * self.SCORE_WEIGHTS["harsh_cornering"] +
            sub_scores["accel_score"] * self.SCORE_WEIGHTS["rapid_accel"] +
            sub_scores["night_score"] * self.SCORE_WEIGHTS["night_driving"]
        )
        composite_score = round(max(10.0, min(100.0, composite_score)), 1)

        # Classification Tiers
        if composite_score >= 88:
            tier = "Elite Safe (Top 15%)"
        elif composite_score >= 75:
            tier = "Low Risk (Preferred)"
        elif composite_score >= 60:
            tier = "Moderate Risk (Standard)"
        elif composite_score >= 45:
            tier = "Elevated Risk (Substandard)"
        else:
            tier = "High Risk (Non-Standard)"

        return {
            "composite_score": composite_score,
            "tier": tier,
            "sub_scores": sub_scores
        }

    def calculate_credibility(self, annual_miles: float) -> float:
        """
        Bühlmann-Straub Actuarial Credibility Z.
        As observed telematics mileage approaches 10,000 miles,
        credibility Z approaches 1.0 (full credibility).
        Formula: Z = sqrt(min(1.0, observed_miles / full_credibility_standard))
        """
        full_credibility_standard = 10000.0
        exposure_ratio = min(1.0, max(0.0, annual_miles / full_credibility_standard))
        z = math.sqrt(exposure_ratio)
        return round(z, 3)

    def calculate_traditional_base_premium(self, telemetry: DriverTelemetryInput) -> float:
        """
        Standard demographic-based actuarial premium (Fixed price).
        Dependent only on age, vehicle value, and territory base.
        """
        base_rate = 1200.0
        
        # Age factor
        if telemetry.driver_age < 21:
            age_factor = 1.65
        elif telemetry.driver_age < 25:
            age_factor = 1.35
        elif telemetry.driver_age > 70:
            age_factor = 1.20
        else:
            age_factor = 1.00

        # Vehicle value factor
        vehicle_factor = (telemetry.vehicle_value / 25000.0) ** 0.65

        # Territory factor
        territory_factor = telemetry.base_location_risk

        fixed_premium = base_rate * age_factor * vehicle_factor * territory_factor
        return round(fixed_premium, 2)

    def calculate_dynamic_premium(
        self,
        telemetry: DriverTelemetryInput,
        weather_risk_factor: float = 1.0
    ) -> PricingBreakdown:
        """
        Full dynamic pricing calculation combining:
        1. Fixed demographic base premium
        2. Pay-As-You-Drive (PAYD) mileage exposure factor
        3. Pay-How-You-Drive (PHYD) telematics driving score multiplier
        4. Credibility weighting (Bühlmann credibility)
        5. Environmental/Weather risk modifier
        """
        trad_fixed = self.calculate_traditional_base_premium(telemetry)
        telematics_res = self.calculate_telematics_score(telemetry)
        score = telematics_res["composite_score"]
        tier = telematics_res["tier"]
        sub_scores = telematics_res["sub_scores"]

        # 1. PAYD Mileage Factor (Linear baseline with 13,500 mi standard)
        mileage_ratio = telemetry.annual_mileage / self.BENCHMARKS["standard_annual_miles"]
        mileage_factor = 0.55 + (0.45 * mileage_ratio)
        mileage_factor = max(0.70, min(1.45, mileage_factor))

        # 2. PHYD Telematics Behavior Multiplier
        if score >= 65:
            uncredited_behavior_mult = 1.0 - ((score - 65.0) / 35.0) * 0.35
        else:
            uncredited_behavior_mult = 1.0 + ((65.0 - score) / 45.0) * 0.45

        # 3. Actuarial Credibility Blending
        z = self.calculate_credibility(telemetry.annual_mileage)
        credited_behavior_mult = (z * uncredited_behavior_mult) + ((1.0 - z) * 1.0)

        # 4. Weather Modifier
        weather_mult = max(0.95, min(1.15, weather_risk_factor))

        # Final Dynamic Premium:
        # Fixed operational & claims overhead (25%) + dynamic risk pool (75%)
        fixed_overhead = trad_fixed * 0.25
        dynamic_loss_pool = trad_fixed * 0.75 * credited_behavior_mult * mileage_factor * weather_mult

        final_dynamic_premium = round(fixed_overhead + dynamic_loss_pool, 2)
        annual_savings = round(trad_fixed - final_dynamic_premium, 2)
        discount_pct = round((annual_savings / trad_fixed) * 100.0, 1)

        # Explainable AI Waterfall Breakdown (Dollar impact of each behavior)
        waterfall = [
            {"component": "Traditional Demographic Base", "impact_dollars": trad_fixed, "type": "base"},
            {"component": "Mileage Exposure Adjustment", "impact_dollars": round(trad_fixed * 0.75 * (mileage_factor - 1.0), 2), "type": "exposure"},
            {"component": "Braking Performance (Hard Decel)", "impact_dollars": round(-trad_fixed * 0.20 * ((sub_scores["braking_score"] - 65) / 100), 2), "type": "behavior"},
            {"component": "Phone Distraction (Screen Focus)", "impact_dollars": round(-trad_fixed * 0.20 * ((sub_scores["distraction_score"] - 65) / 100), 2), "type": "behavior"},
            {"component": "Speed Compliance (>10mph over limit)", "impact_dollars": round(-trad_fixed * 0.15 * ((sub_scores["speeding_score"] - 65) / 100), 2), "type": "behavior"},
            {"component": "Harsh Cornering & Acceleration", "impact_dollars": round(-trad_fixed * 0.10 * (((sub_scores["cornering_score"] + sub_scores["accel_score"])/2 - 65) / 100), 2), "type": "behavior"},
            {"component": "Nighttime Driving Risk (12am-4am)", "impact_dollars": round(-trad_fixed * 0.08 * ((sub_scores["night_score"] - 65) / 100), 2), "type": "behavior"},
            {"component": "Real-time Weather Risk Modifier", "impact_dollars": round(trad_fixed * (weather_mult - 1.0), 2), "type": "environmental"},
            {"component": "Final Personalized Telematics Premium", "impact_dollars": final_dynamic_premium, "type": "final"}
        ]

        fairness_metrics = {
            "fairness_index": round(min(1.0, (score / 100.0) * (1.0 / max(0.5, credited_behavior_mult))), 2),
            "unjust_penalty_saved": annual_savings if annual_savings > 0 else 0.0,
            "adverse_selection_protection": "High (Self-Selecting Safe Pool)" if score >= 75 else "Protected via Surcharge"
        }

        return PricingBreakdown(
            driver_score=score,
            score_tier=tier,
            traditional_fixed_premium=trad_fixed,
            dynamic_ubi_premium=final_dynamic_premium,
            monthly_dynamic_premium=round(final_dynamic_premium / 12.0, 2),
            annual_savings=annual_savings,
            discount_percentage=discount_pct,
            credibility_factor=z,
            sub_scores=sub_scores,
            waterfall_breakdown=waterfall,
            fairness_metrics=fairness_metrics
        )
