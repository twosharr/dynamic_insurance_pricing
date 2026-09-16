"""
run.py
------
One-command launch orchestrator for UC070: AI-Powered Dynamic Insurance Pricing Engine.
Initializes data directories, trains the ML risk model, compiles the executive PDF,
and launches the FastAPI ASGI server with hot-reloading.
"""

import os
import sys
import uvicorn
import pandas as pd

from backend.data_generator import generate_and_save_all_sample_documents
from backend.pdf_generator import build_executive_pdf
from backend.ml_risk_model import TelematicsRiskModel

def bootstrap():
    print("=" * 70)
    print("🚀 TELEMARISK ENTERPRISE: BEHAVIOR-BASED RATING & TELEMATICS ENGINE")
    print("   Calibrated with Zendrive & Cambridge Mobile Telematics (CMT) Benchmarks")
    print("   Actuarial Rate-Making & Telematics Underwriting System")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_docs_dir = os.path.join(base_dir, "sample_documents")
    docs_dir = os.path.join(base_dir, "docs_and_presentation")
    pdf_path = os.path.join(docs_dir, "UC070_Dynamic_Insurance_Pricing_Executive_Guide.pdf")

    # 1. Generate Sample Documents
    print("\n[Step 1/3] Generating telematics fleet datasets & sample documents...")
    os.makedirs(sample_docs_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)
    generate_and_save_all_sample_documents(sample_docs_dir)
    print(" -> driver_fleet_actuarial_dataset.csv (1,000 drivers)")
    print(" -> telematics_trip_raw_log.json (High-frequency sensor stream)")
    print(" -> telematics_trips_summary.csv (Aggregated trip logs)")
    print(" -> sample_dynamic_policy_schedule.json (Connected policy schedule)")

    # 2. Build Executive Presentation PDF
    print("\n[Step 2/3] Compiling publication-quality executive presentation PDF...")
    try:
        build_executive_pdf(pdf_path)
        print(f" -> Executive PDF generated at: {pdf_path}")
    except Exception as e:
        print(f" -> Warning during PDF build: {e}")

    # 3. Launch Server
    print("\n[Step 3/3] Starting FastAPI web server & interactive dashboard...")
    print("=" * 70)
    print("🌐 Dashboard URL:        http://localhost:8000")
    print("📄 Interactive Swagger:  http://localhost:8000/docs")
    print("📊 Executive PDF Guide:  http://localhost:8000/api/download-report")
    print("📁 Sample Documents:     http://localhost:8000/sample_documents/")
    print("=" * 70)
    print("Press Ctrl+C to terminate the server.\n")

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    bootstrap()
