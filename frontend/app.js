/**
 * app.js
 * TelemaRisk Enterprise Underwriting Console
 * Client-side orchestration for behavior-based rating, spatial telematics, and fleet analytics.
 */

// Global State
let currentSimulationData = null;
let mapInstance = null;
let routePolyline = null;
let carMarker = null;
let tripWaypoints = [];
let simInterval = null;
let currentSimStep = 0;
let debounceTimer = null;

// Standardized Driver Risk Profiles
const ARCHETYPES = {
  safe: {
    braking: 0.8,
    distraction: 0.5,
    speeding: 2.0,
    mileage: 10500,
    cornering: 0.6,
    night: 3,
    age: 34,
    veh_val: 32000
  },
  weekend: {
    braking: 1.4,
    distraction: 1.2,
    speeding: 3.5,
    mileage: 4800,
    cornering: 0.8,
    night: 5,
    age: 42,
    veh_val: 26000
  },
  night: {
    braking: 1.8,
    distraction: 2.0,
    speeding: 5.0,
    mileage: 13000,
    cornering: 1.2,
    night: 52,
    age: 29,
    veh_val: 24000
  },
  distracted: {
    braking: 4.2,
    distraction: 9.5,
    speeding: 12.0,
    mileage: 11500,
    cornering: 3.2,
    night: 12,
    age: 27,
    veh_val: 29000
  },
  speedster: {
    braking: 6.8,
    distraction: 6.0,
    speeding: 32.0,
    mileage: 17000,
    cornering: 4.5,
    night: 22,
    age: 23,
    veh_val: 35000
  }
};

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
  // Initialize calculation
  updateSimulation();
  // Fetch fleet dataset
  loadFleetData();
});

// Functional Tab Navigation
function switchTab(tabId) {
  const tabs = ["simulator", "map-view", "fleet"];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab-${t}`);
    const view = document.getElementById(`view-${t}`);
    if (t === tabId) {
      if (btn) btn.classList.add("active");
      if (view) view.classList.remove("hidden");
    } else {
      if (btn) btn.classList.remove("active");
      if (view) view.classList.add("hidden");
    }
  });

  if (tabId === "map-view") {
    setTimeout(initMapIfNeeded, 200);
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Load Pre-configured Risk Profile
function loadArchetype(key) {
  const arch = ARCHETYPES[key];
  if (!arch) return;

  document.getElementById("input-braking").value = arch.braking;
  document.getElementById("input-distraction").value = arch.distraction;
  document.getElementById("input-speeding").value = arch.speeding;
  document.getElementById("input-mileage").value = arch.mileage;
  document.getElementById("input-cornering").value = arch.cornering;
  document.getElementById("input-night").value = arch.night;
  document.getElementById("input-age").value = arch.age;
  document.getElementById("input-veh-val").value = arch.veh_val;

  updateSimulation();
}

// Live Rating Recalculation
function updateSimulation() {
  const braking = parseFloat(document.getElementById("input-braking").value);
  const distraction = parseFloat(document.getElementById("input-distraction").value);
  const speeding = parseFloat(document.getElementById("input-speeding").value);
  const mileage = parseFloat(document.getElementById("input-mileage").value);
  const cornering = parseFloat(document.getElementById("input-cornering").value);
  const night = parseFloat(document.getElementById("input-night").value);
  const age = parseInt(document.getElementById("input-age").value) || 35;
  const vehVal = parseFloat(document.getElementById("input-veh-val").value) || 28000;

  document.getElementById("val-braking").innerText = `${braking.toFixed(1)} / 100 mi`;
  document.getElementById("val-distraction").innerText = `${distraction.toFixed(1)} min / hr`;
  document.getElementById("val-speeding").innerText = `${speeding.toFixed(1)}% of trip`;
  document.getElementById("val-mileage").innerText = `${mileage.toLocaleString()} miles / yr`;
  document.getElementById("val-cornering").innerText = `${cornering.toFixed(1)} / 100mi`;
  document.getElementById("val-night").innerText = `${night}% miles`;

  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchPricingFromBackend({
      annual_mileage: mileage,
      hard_braking_per_100mi: braking,
      rapid_accel_per_100mi: 2.0,
      speeding_pct_of_time: speeding,
      phone_distraction_min_per_hr: distraction,
      harsh_cornering_per_100mi: cornering,
      night_driving_pct: night,
      driver_age: age,
      vehicle_value: vehVal,
      weather_risk_factor: 1.0
    });
  }, 100);
}

// Backend API Call: Calculate Rating
async function fetchPricingFromBackend(payload) {
  try {
    const res = await fetch("/api/calculate-premium", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Rating API execution failed");
    const data = await res.json();
    renderPricingResults(data);
  } catch (err) {
    console.warn("API request failed:", err);
  }
}

// Render Results to UI
function renderPricingResults(data) {
  const p = data.pricing;
  const ml = data.ml_risk;

  document.getElementById("card-traditional-premium").innerText = `$${p.traditional_fixed_premium.toFixed(2)}`;
  document.getElementById("card-dynamic-premium").innerText = `$${p.dynamic_ubi_premium.toFixed(2)}`;
  document.getElementById("card-monthly-rate").innerText = `$${p.monthly_dynamic_premium.toFixed(2)} / month`;

  const banner = document.getElementById("savings-banner");
  const title = document.getElementById("savings-title");
  const desc = document.getElementById("savings-desc");
  const badge = document.getElementById("savings-badge");

  if (p.annual_savings >= 0) {
    banner.className = "p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-between";
    title.innerText = `Net Annual Policyholder Credit: $${p.annual_savings.toFixed(2)}`;
    desc.innerText = `${p.discount_percentage.toFixed(1)}% favorable rate adjustment`;
    badge.className = "px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-xs font-bold font-mono";
    badge.innerText = `-${p.discount_percentage.toFixed(1)}%`;
  } else {
    const surcharge = Math.abs(p.annual_savings);
    banner.className = "p-3 rounded-xl bg-red-500/10 border border-red-500/25 flex items-center justify-between";
    title.innerText = `Actuarial Risk Surcharge: +$${surcharge.toFixed(2)}`;
    desc.innerText = `${Math.abs(p.discount_percentage).toFixed(1)}% risk debit based on observed driving exposure`;
    badge.className = "px-2 py-0.5 rounded bg-red-500/20 text-red-300 text-xs font-bold font-mono";
    badge.innerText = `+${Math.abs(p.discount_percentage).toFixed(1)}%`;
  }

  // Radial SVG Gauge
  const score = p.driver_score;
  document.getElementById("gauge-score").innerText = score.toFixed(1);
  const circle = document.getElementById("gauge-circle");
  const circumference = 2 * Math.PI * 32; // 201.06
  const offset = circumference - (score / 100.0) * circumference;
  circle.style.strokeDashoffset = offset;

  let color = "#059669"; // emerald
  if (score < 45) color = "#DC2626";      // red
  else if (score < 60) color = "#EA580C"; // orange
  else if (score < 75) color = "#D97706"; // amber
  else if (score < 88) color = "#2563EB"; // blue
  circle.style.stroke = color;

  const tierBadge = document.getElementById("tier-badge");
  tierBadge.innerText = p.score_tier;
  if (score >= 88) tierBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold badge-elite inline-block";
  else if (score >= 75) tierBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold badge-low inline-block";
  else if (score >= 60) tierBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold badge-moderate inline-block";
  else tierBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold badge-high inline-block";

  document.getElementById("val-credibility").innerText = `${p.credibility_factor.toFixed(3)} (${(p.credibility_factor * 100).toFixed(1)}%)`;
  if (ml) {
    document.getElementById("val-claim-prob").innerText = `${ml.predicted_claim_probability.toFixed(1)}% / yr`;
    document.getElementById("val-risk-grade").innerText = ml.actuarial_risk_grade;
  }

  // Update Sub-Score Metrics Breakdown
  if (p.sub_scores) {
    const s = p.sub_scores;
    const updateSub = (id, val, barId) => {
      const el = document.getElementById(id);
      const bar = document.getElementById(barId);
      if (el) el.innerText = `${val.toFixed(1)} / 100`;
      if (bar) bar.style.width = `${Math.max(5, Math.min(100, val))}%`;
    };
    updateSub("subscore-braking", s.braking_score, "bar-subscore-braking");
    updateSub("subscore-distraction", s.distraction_score, "bar-subscore-distraction");
    updateSub("subscore-speeding", s.speeding_score, "bar-subscore-speeding");
    updateSub("subscore-cornering", s.cornering_score, "bar-subscore-cornering");
    updateSub("subscore-accel", s.accel_score, "bar-subscore-accel");
    updateSub("subscore-night", s.night_score, "bar-subscore-night");
  }

  renderWaterfall(p.waterfall_breakdown);
}

// Render Rating Factor Attribution
function renderWaterfall(breakdown) {
  const container = document.getElementById("waterfall-container");
  if (!container || !breakdown) return;

  container.innerHTML = "";

  breakdown.forEach(item => {
    const isBase = item.type === "base";
    const isFinal = item.type === "final";
    const dollars = item.impact_dollars;

    let barColor = "bg-blue-600";
    let displayDollars = "";

    if (isBase) {
      barColor = "bg-gray-600";
      displayDollars = `$${dollars.toFixed(2)}`;
    } else if (isFinal) {
      barColor = "bg-emerald-500";
      displayDollars = `$${dollars.toFixed(2)}`;
    } else if (dollars < 0) {
      barColor = "bg-emerald-500";
      displayDollars = `-$${Math.abs(dollars).toFixed(2)} (Credit)`;
    } else if (dollars > 0) {
      barColor = "bg-rose-500";
      displayDollars = `+$${dollars.toFixed(2)} (Debit)`;
    } else {
      barColor = "bg-gray-700";
      displayDollars = "$0.00 (Neutral)";
    }

    const row = document.createElement("div");
    row.className = "flex items-center justify-between text-xs py-1.5 px-2.5 rounded bg-gray-900/40 border border-gray-800/60";
    row.innerHTML = `
      <div class="flex items-center space-x-2.5 w-1/2">
        <span class="w-2 h-2 rounded-sm ${barColor}"></span>
        <span class="text-gray-300 font-medium">${item.component}</span>
      </div>
      <div class="w-1/2 flex items-center justify-end space-x-3">
        <div class="w-28 bg-gray-800 rounded-full h-1.5 overflow-hidden hidden sm:block">
          <div class="${barColor} h-1.5" style="width: ${Math.min(100, Math.max(15, (Math.abs(dollars)/280)*100))}%"></div>
        </div>
        <span class="font-mono font-semibold ${dollars < 0 ? 'text-emerald-400' : (dollars > 0 ? (isFinal ? 'text-white' : 'text-rose-400') : 'text-gray-400')}">
          ${displayDollars}
        </span>
      </div>
    `;
    container.appendChild(row);
  });
}

// Leaflet Map Initialization strictly on Highway 101 on land
function initMapIfNeeded() {
  if (mapInstance) {
    mapInstance.invalidateSize();
    return;
  }

  const mapContainer = document.getElementById("map");
  if (!mapContainer) return;

  // Center on US-101 Corridor
  mapInstance = L.map("map").setView([37.6258, -122.3995], 11);

  // CartoDB Dark Matter or OpenStreetMap
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(mapInstance);

  fetchTripData();
}

// Fetch Trip Telemetry from Backend
async function fetchTripData() {
  try {
    const res = await fetch("/api/simulate-trip");
    const data = await res.json();
    currentSimulationData = data;
    tripWaypoints = data.telemetry_points || [];

    plotRouteOnMap(data);
    renderEventsTimeline(data.events || []);
  } catch (err) {
    console.error("Failed to load trajectory data", err);
  }
}

// Plot Polyline & Hazard Pins on Map
function plotRouteOnMap(tripData) {
  if (!mapInstance || !tripWaypoints.length) return;

  const latlngs = tripWaypoints.map(p => [p.latitude, p.longitude]);
  
  if (routePolyline) mapInstance.removeLayer(routePolyline);
  routePolyline = L.polyline(latlngs, {
    color: "#2563EB",
    weight: 4,
    opacity: 0.9,
    smoothFactor: 1
  }).addTo(mapInstance);

  mapInstance.fitBounds(routePolyline.getBounds(), { padding: [35, 35] });

  const startPt = latlngs[0];
  const endPt = latlngs[latlngs.length - 1];

  L.marker(startPt).addTo(mapInstance).bindPopup("<b>Transit Origin:</b> US-101 South / SOMA Ramp");
  L.marker(endPt).addTo(mapInstance).bindPopup("<b>Transit Destination:</b> Palo Alto University Ave");

  (tripData.events || []).forEach(evt => {
    let pinColor = "#DC2626";
    if (evt.type.includes("Speed")) pinColor = "#D97706";
    else if (evt.type.includes("Phone") || evt.type.includes("Distraction")) pinColor = "#9333EA";

    const customIcon = L.divIcon({
      className: "hazard-pin",
      html: `<div style="background-color:${pinColor}; width:12px; height:12px; border-radius:50%; border:2px solid white; box-shadow:0 0 8px ${pinColor};"></div>`,
      iconSize: [12, 12]
    });

    L.marker([evt.lat, evt.lon], { icon: customIcon }).addTo(mapInstance)
      .bindPopup(`<b>${evt.type}</b><br><span style="font-size:11px">${evt.severity}</span><br><span style="font-size:11px; color:#94A3B8">${evt.message}</span>`);
  });

  const carIcon = L.divIcon({
    className: "car-sim-marker",
    html: `<div style="background-color:#059669; width:16px; height:16px; border-radius:50%; border:3px solid white; box-shadow:0 0 10px #059669;"></div>`,
    iconSize: [16, 16]
  });
  carMarker = L.marker(startPt, { icon: carIcon }).addTo(mapInstance);
}

// Render Telematics Incidents Log
function renderEventsTimeline(events) {
  const container = document.getElementById("events-timeline");
  if (!container) return;

  container.innerHTML = "";
  events.forEach(evt => {
    const isBraking = evt.type.includes("Braking");
    const isPhone = evt.type.includes("Phone") || evt.type.includes("Distraction");
    const badgeColor = isBraking ? "text-red-400 border-red-500/30 bg-red-500/10" : (isPhone ? "text-purple-400 border-purple-500/30 bg-purple-500/10" : "text-amber-400 border-amber-500/30 bg-amber-500/10");

    const item = document.createElement("div");
    item.className = "p-2.5 rounded-lg bg-gray-900/70 border border-gray-800 flex items-center justify-between text-xs";
    item.innerHTML = `
      <div class="flex items-center space-x-2.5">
        <span class="px-2 py-0.5 rounded border text-[10px] font-semibold uppercase tracking-wider ${badgeColor}">${evt.type}</span>
        <span class="text-gray-300">${evt.message}</span>
      </div>
      <span class="text-gray-400 text-[10px] font-mono whitespace-nowrap pl-2">${evt.severity}</span>
    `;
    container.appendChild(item);
  });
}

// Trajectory Playback
function toggleRouteSimulation() {
  const playText = document.getElementById("play-text");

  if (simInterval) {
    clearInterval(simInterval);
    simInterval = null;
    playText.innerText = "Resume Playback";
  } else {
    playText.innerText = "Pause Playback";
    simInterval = setInterval(() => {
      if (currentSimStep >= tripWaypoints.length) {
        clearInterval(simInterval);
        simInterval = null;
        playText.innerText = "Restart Playback";
        currentSimStep = 0;
        return;
      }

      const pt = tripWaypoints[currentSimStep];
      if (carMarker) carMarker.setLatLng([pt.latitude, pt.longitude]);

      document.getElementById("hud-speed").innerText = `${pt.speed_mph.toFixed(1)} mph`;
      document.getElementById("hud-gforce").innerText = `${pt.accel_g >= 0 ? '+' : ''}${pt.accel_g.toFixed(2)} g`;
      document.getElementById("hud-phone").innerText = pt.phone_screen_on ? "Screen Active" : "Inactive";
      document.getElementById("hud-phone").className = `text-base font-bold ${pt.phone_screen_on ? 'text-rose-400' : 'text-emerald-400'}`;

      currentSimStep++;
    }, 200);
  }
}

function resetRouteSimulation() {
  if (simInterval) {
    clearInterval(simInterval);
    simInterval = null;
  }
  currentSimStep = 0;
  if (tripWaypoints.length > 0 && carMarker) {
    carMarker.setLatLng([tripWaypoints[0].latitude, tripWaypoints[0].longitude]);
  }
  document.getElementById("play-text").innerText = "Start Trajectory Playback";
}

// Load Fleet Data for Table
async function loadFleetData() {
  try {
    const res = await fetch("/api/drivers");
    const data = await res.json();
    const tbody = document.getElementById("fleet-table-body");
    if (!tbody || !data.sample_drivers) return;

    tbody.innerHTML = "";
    data.sample_drivers.forEach(d => {
      const isSaving = d.annual_savings > 0;
      const tr = document.createElement("tr");
      tr.className = "hover:bg-gray-800/40 transition";
      tr.innerHTML = `
        <td class="py-2.5 px-3 font-mono text-gray-400">${d.driver_id}</td>
        <td class="py-2.5 px-3 font-medium text-white">${d.archetype}</td>
        <td class="py-2.5 px-3">${d.hard_braking_per_100mi}</td>
        <td class="py-2.5 px-3">${d.phone_distraction_min_hr}m</td>
        <td class="py-2.5 px-3">${d.speeding_pct}%</td>
        <td class="py-2.5 px-3 font-bold text-blue-400">${d.driving_score}</td>
        <td class="py-2.5 px-3 text-gray-400">$${d.traditional_premium.toFixed(0)}</td>
        <td class="py-2.5 px-3 font-semibold text-white">$${d.dynamic_ubi_premium.toFixed(0)}</td>
        <td class="py-2.5 px-3 font-semibold ${isSaving ? 'text-emerald-400' : 'text-rose-400'}">
          ${isSaving ? '-' : '+'}$${Math.abs(d.annual_savings).toFixed(0)} (${d.discount_pct > 0 ? '-' : '+'}${Math.abs(d.discount_pct).toFixed(0)}%)
        </td>
        <td class="py-2.5 px-3">
          <button onclick="loadDriverIntoSimulator(${JSON.stringify(d).replace(/"/g, '&quot;')})" class="text-xs text-blue-400 hover:text-blue-300 underline font-sans">
            Load Profile
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load fleet data", err);
  }
}

function loadDriverIntoSimulator(d) {
  document.getElementById("input-braking").value = d.hard_braking_per_100mi;
  document.getElementById("input-distraction").value = d.phone_distraction_min_hr;
  document.getElementById("input-speeding").value = d.speeding_pct;
  document.getElementById("input-mileage").value = d.annual_mileage;
  document.getElementById("input-cornering").value = d.harsh_cornering_per_100mi;
  document.getElementById("input-night").value = d.night_driving_pct;
  document.getElementById("input-age").value = d.driver_age;
  document.getElementById("input-veh-val").value = d.vehicle_value;

  switchTab("simulator");
  updateSimulation();
}
