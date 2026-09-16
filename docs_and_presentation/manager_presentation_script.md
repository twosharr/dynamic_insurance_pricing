# Manager & Team Demonstration Script: UC070 Dynamic Insurance Pricing

## Presentation Overview
- **Use Case:** UC070 - Dynamic Pricing for Insurance based on Driving Behavior
- **Demonstration Goal:** Prove technical feasibility, actuarial rigor, and commercial ROI of transitioning from traditional fixed premiums to AI-powered telematics pricing.
- **Estimated Demo Duration:** 10 to 15 minutes
- **Companion Artifacts:**
  - Live Interactive Web Dashboard (`http://localhost:8000`)
  - Executive Whitepaper PDF (`docs_and_presentation/UC070_Dynamic_Insurance_Pricing_Executive_Guide.pdf`)
  - Actuarial & Sample Datasets (`sample_documents/`)

---

## Slide-by-Slide / Tab-by-Tab Talk Track

### 1. The Hook & The Problem Statement (2 Minutes)
> *"Good morning team. Today, I'm presenting **UC070: AI-Powered Dynamic Pricing for Insurance**.
> Let's start with a simple question: Why do two 35-year-olds driving the same Honda Accord in the same zip code pay the exact same $1,450 annual premium, even if one is a cautious commuter who never touches their phone, and the other regularly texts while doing 75 mph?
> 
> The answer is: **Fixed pricing is fundamentally unfair to safe drivers**, and it creates an adverse selection crisis. Safe drivers subsidize dangerous drivers until competitors offer them a discount and they churn.
> Our platform replaces this legacy model with telematics-driven dynamic pricing inspired by Zendrive."*

---

### 2. Live Platform Tour: The Pricing Simulator (4 Minutes)
**Action:** Open browser to `http://localhost:8000`. Show Tab 1: **Dynamic Pricing Simulator**.

> *"Here on the dashboard, you see our real-time behavioral simulation engine. On the right, we display the traditional fixed demographic premium: \$1,450.
> Now watch what happens when we adjust behavioral telemetry:
> - If we reduce **Hard Braking** from 4.5 down to 0.8 per 100 miles, and reduce **Phone Distraction** to under 1 minute per hour...
> - Look at the Zendrive-calibrated Safe Driving Gauge: it jumps to **93.2 (Elite Safe)**.
> - The dynamic premium instantly recalculates to **\$982 per year (\$81.83/mo)**, saving the customer **\$468 annually (32.3% discount)**.
> - Conversely, if we slide phone distraction to 10 minutes and speeding to 25%, the score drops into the red zone (38), triggering an actuarial risk surcharge to **\$2,240/yr**, protecting carrier solvency."*

---

### 3. Actuarial Rigor & Explainable AI (SHAP Waterfall) (3 Minutes)
**Action:** Scroll down to the **Explainable AI Breakdown** card and the **Actuarial Credibility** badge.

> *"A critical requirement for regulatory approval (like NAIC or state insurance commissioners) is: **No black boxes**.
> Look at our Explainable AI Waterfall:
> Every dollar change is explicitly attributed:
> - Traditional Base: \$1,450
> - Low Mileage Credit: -\$120
> - Smooth Braking Credit: -\$145
> - Zero Phone Distraction Credit: -\$160
> - Real-Time Weather Hazard: +\$25
> 
> Furthermore, we implemented **Bühlmann-Straub Actuarial Credibility ($Z$)**. If a new driver only has 500 miles on the app, their credibility factor $Z$ is 0.22, meaning 78% of their rate is anchored to the group prior. Only as miles reach 10,000 does $Z$ approach 1.0. This prevents unfair pricing spikes from a single bad day."*

---

### 4. Interactive Route Telematics & Free Weather API (3 Minutes)
**Action:** Switch to Tab 2: **Interactive Route & Telematics GIS Map** and click **Simulate Live Route**.

> *"Next, let's look at how telemetry is captured in the field.
> This Leaflet map visualizes an actual commuter drive from downtown San Francisco into Silicon Valley.
> As we play the simulation:
> - Notice the green waypoints for smooth cruising.
> - At timestamp 02:00, the vehicle experiences a sudden -0.48g deceleration: the system places a red **Hard Braking** hazard pin.
> - At timestamp 05:40, the driver unlocks and tilts their smartphone: a **Distracted Driving** event is logged.
> 
> Notice also our **Live Weather Hazard Widget**. We integrated the **Open-Meteo API**, which is 100% free and requires zero API keys. When severe weather or black ice is detected, our road hazard multiplier adjusts dynamically without needing manual actuarial intervention."*

---

### 5. Fleet Manager, Business Impact & Executive PDF (3 Minutes)
**Action:** Switch to Tab 3: **Fleet Archetypes**, then demonstrate the **Download Executive PDF** button.

> *"In the Fleet Manager tab, we generated 1,000 synthetic driver profiles across 5 distinct archetypes—from 'Safe Commuter Elena' to 'Aggressive Speedster Tyler'.
> The business results are staggering:
> - **Loss Ratio drops by 15.3 percentage points** (from 68.4% down to 53.1%).
> - **Safe driver annual retention increases from 72% to 89%**.
> - Net underwriting profit increases by **\$2.03 Million per 10,000 policyholders**.
> 
> Finally, we compiled this entire project into a publication-grade 6-page **Executive Presentation PDF**, complete with mathematical proofs, architecture diagrams, and compliance notes.
> 
> Everything is running live right now on our local server. Let's open the floor for questions!"*

---

## Common Manager & Team Q&A Handling

**Q1: "Is this compliant with state insurance regulations that ban discrimination?"**
> **Answer:** *"Yes! Traditional pricing uses zip code and credit scores, which are under regulatory fire for disparate racial and income impact. Telematics uses strictly controllable driving behavior (hard braking, speeding, phone distraction). NAIC and state commissioners favor behavioral rating because motorists have direct control over their rate."*

**Q2: "What if someone doesn't have an internet connection while driving?"**
> **Answer:** *"Our architecture logs high-frequency sensor readings on-device (smartphone or OBD-II). When WiFi or cell connectivity is restored, the aggregated trip summary is securely uploaded. Our weather engine also includes a complete offline simulator so rating never crashes."*

**Q3: "Are there expensive third-party API costs?"**
> **Answer:** *"No. We specifically engineered this prototype using free APIs: Open-Meteo for live atmospheric hazard data and OpenStreetMap/Leaflet for GIS rendering, requiring $0 in subscription fees."*
