# Actuarial Pricing Model Specification: UC070 Telematics UBI Engine

## 1. Scope & Business Objective
This document outlines the mathematical, statistical, and actuarial rating framework for **Usage-Based Auto Insurance (UBI)** combining:
- **Pay-As-You-Drive (PAYD):** Mileage-based risk exposure.
- **Pay-How-You-Drive (PHYD):** Behavioral telematics scoring inspired by **Zendrive** and **Cambridge Mobile Telematics (CMT)**.
- **Environmental Road Risk Adjustment:** Real-time meteorological hazard modifiers using the **Open-Meteo API**.

Traditional static rate-making relies on immutable demographic proxies (age, sex, territory, credit tier). This specification establishes a dynamic behavioral pricing framework compliant with National Association of Insurance Commissioners (NAIC) standards and European EIOPA fairness guidelines.

---

## 2. Actuarial Pure Premium Formulation
Under classical actuarial risk theory, the expected pure loss cost $E[L]$ for a policyholder $i$ is decomposed into claim frequency and claim severity:

$$E[L_i] = \lambda_i \times \mu_i$$

Where:
- $\lambda_i$: Expected claim frequency per year (modeled via Poisson or Negative Binomial GLM).
- $\mu_i$: Expected claim severity given that a claim occurred (modeled via Gamma or Log-Normal GLM).

In this telematics engine, the baseline pure premium $P_{\text{base}}$ is determined from conventional demographic variables, and the dynamic telematics multiplier $M_{\text{dynamic}}$ modifies the loss cost pool:

$$P_{\text{dynamic}} = P_{\text{fixed-overhead}} + \left( P_{\text{risk-pool}} \times M_{\text{telematics}} \times M_{\text{mileage}} \times M_{\text{weather}} \right)$$

Where:
- $P_{\text{fixed-overhead}} = 0.25 \times P_{\text{traditional}}$ (Non-risk operational, acquisition, and administrative expenses).
- $P_{\text{risk-pool}} = 0.75 \times P_{\text{traditional}}$ (Actuarial pure risk reserve).

---

## 3. Telematics Scoring Algorithm (Zendrive-Calibrated)

Raw high-frequency telemetry (10 Hz accelerometers, gyroscopes, and GPS logs) is filtered and aggregated into six core behavioral features:

| Metric Name | Mathematical Definition / Trigger | Weight ($w_k$) | Benchmark Good | Benchmark Poor |
| :--- | :--- | :--- | :--- | :--- |
| **Hard Deceleration ($S_{\text{brake}}$)** | Longitudinal decel $< -0.40g$ ($-3.92 \text{ m/s}^2$) | 25% | $\le 1.0$ / 100 mi | $\ge 6.0$ / 100 mi |
| **Phone Distraction ($S_{\text{distract}}$)** | Screen active + movement $> 15^\circ$ tilt | 25% | $\le 1.0$ min/hr | $\ge 12.0$ min/hr |
| **Excessive Speeding ($S_{\text{speed}}$)** | GPS Speed $> \text{Posted Limit} + 10 \text{ mph}$ | 20% | $\le 3.0\%$ of trip | $\ge 25.0\%$ of trip |
| **Harsh Cornering ($S_{\text{corner}}$)** | Lateral acceleration $> 0.38g$ | 10% | $\le 0.8$ / 100 mi | $\ge 5.0$ / 100 mi |
| **Rapid Acceleration ($S_{\text{accel}}$)** | Longitudinal accel $> +0.35g$ ($+3.43 \text{ m/s}^2$) | 10% | $\le 1.0$ / 100 mi | $\ge 5.0$ / 100 mi |
| **Nighttime Driving ($S_{\text{night}}$)** | Exposure between 12:00 AM - 4:00 AM | 10% | $\le 4.0\%$ miles | $\ge 25.0\%$ miles |

### Normalization Function
Each observed metric $x_k$ is mapped to a normalized sub-score $S_k \in [0, 100]$:
$$S_k = \max\left(0, \min\left(100, 100 - \left(\frac{x_k - \text{good}_k}{\text{poor}_k - \text{good}_k}\right) \times 80\right)\right)$$

The **Composite Zendrive Driving Score** $S_{\text{composite}}$ is:
$$S_{\text{composite}} = \sum_{k=1}^{6} w_k \cdot S_k$$

### Safety Classification Tiers:
- **Elite Safe (Top 15%):** Score $\ge 88 \implies$ Maximum discount tier (-30% to -35%).
- **Low Risk (Preferred):** Score $75 - 87 \implies$ Standard discount tier (-15% to -25%).
- **Moderate Risk (Standard):** Score $60 - 74 \implies$ Baseline rate (-5% to +5%).
- **Elevated Risk (Substandard):** Score $45 - 59 \implies$ Surcharge tier (+10% to +25%).
- **High Risk (Non-Standard):** Score $< 45 \implies$ High risk surcharge tier (+30% to +45%).

---

## 4. Actuarial Credibility Theory (Bühlmann-Straub Model)
To prevent pricing volatility and unjust penalties during early policy periods, the telematics behavioral multiplier is credibility-weighted using the **Bühlmann Credibility Model**:

$$Z = \sqrt{\min\left(1.0, \frac{\text{Miles}_{\text{observed}}}{\text{Standard}_{\text{full}}}\right)}$$

Where $\text{Standard}_{\text{full}} = 10,000 \text{ miles}$.

The credited behavioral multiplier is:
$$M_{\text{credited}} = Z \cdot M_{\text{observed}} + (1 - Z) \cdot 1.00$$

This guarantees that:
- A new driver with only 500 miles has $Z = 0.22$; their premium is predominantly anchored to the collective prior mean.
- A veteran telematics driver with 10,000+ miles has $Z = 1.00$; their premium is 100% personalized.

---

## 5. Pay-As-You-Drive (PAYD) Mileage Factor
Accident probability is strictly non-linearly dependent on road exposure miles. Based on empirical actuarial curves:

$$M_{\text{mileage}} = 0.55 + 0.45 \times \left( \frac{\text{Annual Miles}}{13,500} \right)$$
Bounded within $[0.70, 1.45]$.

---

## 6. Real-Time Weather Hazard Risk Multiplier
Integrated with Open-Meteo free atmospheric API:
- **Dry Road (Baseline):** $M_{\text{weather}} = 1.00$
- **Moderate Wet Pavement (Rain 1.0 - 5.0 mm/hr):** $M_{\text{weather}} = 1.06$
- **Heavy Rain / Hydroplaning (Rain > 5.0 mm/hr):** $M_{\text{weather}} = 1.12$
- **Snow / Black Ice (Snowfall or Temp $\le 1^\circ\text{C}$ with moisture):** $M_{\text{weather}} = 1.18 - 1.25$
- **Severe Crosswinds ($> 45 \text{ km/h}$):** $M_{\text{weather}} = 1.07$

---

## 7. Regulatory & Fairness Compliance
- **Non-Discrimination:** Rating factors are strictly behavioral and controllable by the driver, eliminating indirect racial and socioeconomic redlining associated with zip codes and credit scores.
- **Transparency & FCRA Compliance:** Every policyholder statement contains an itemized Explainable AI breakdown displaying the exact dollar contribution of each behavioral metric.
- **Data Minimization (GDPR / CCPA):** Continuous GPS waypoints are discarded after trip feature aggregation; only statistical risk aggregates are retained for rating.
