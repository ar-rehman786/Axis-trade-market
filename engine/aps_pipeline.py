# aps_pipeline.py - Complete Pipeline with Black Kit
"""
APS Market Intelligence Pipeline
Processes CSV → Normalizes → Scores → Health Check → Black Kit PDF
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

from aps_config import INPUT_DIR, OUTPUT_DIR
from aps_normalize import normalize_and_score
from aps_healthcheck import health_check
from aps_render import render_pdf
from aps_black_kit import generate_aps_filename

def extract_market_info(df):
    """Extract market name, quarter, year from data"""
    market_name = "Raleigh, NC"  # Default
    
    if 'City' in df.columns and 'State' in df.columns:
        cities = df['City'].value_counts()
        states = df['State'].value_counts()
        if len(cities) > 0 and len(states) > 0:
            top_city = cities.index[0]
            top_state = states.index[0]
            market_name = f"{top_city}, {top_state}"
    
    # Extract quarter and year from current date
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    year = now.year
    
    return market_name, quarter, year

def main(csv_path: str):
    """
    Main pipeline execution
    
    Steps:
    1. Load CSV
    2. Normalize and score data
    3. Run 18-point health check
    4. Save scored CSV
    5. Generate Black Kit PDF (7 pages)
    """
    csv_path = Path(csv_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("APS MARKET INTELLIGENCE PIPELINE")
    print("="*60)
    print(f"\n📁 Input file: {csv_path.name}")
    
    # Step 1: Load CSV
    print("\n[1/5] Loading CSV...")
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    print(f"  ✓ Loaded {len(df):,} records")
    print(f"  ✓ Found {len(df.columns)} columns")
    
    # Step 2: Normalize and score
    print("\n[2/5] Normalizing and scoring data...")
    df = normalize_and_score(df)
    print("  ✓ Calculated LTV, Equity, Loan Age")
    print("  ✓ Calculated APS Score v2.0")
    print("  ✓ Assigned APS Tiers")
    print("  ✓ Calculated CCI Index")
    
    # Step 3: Health check
    print("\n[3/5] Running 18-point health check...")
    hc = health_check(df)
    
    print("\n" + "-"*60)
    print("HEALTH CHECK RESULTS")
    print("-"*60)
    
    pass_count = sum(1 for v in hc.values() if v.get('status') == 'PASS')
    warn_count = sum(1 for v in hc.values() if v.get('status') == 'WARN')
    fail_count = sum(1 for v in hc.values() if v.get('status') == 'FAIL')
    
    for check_name, result in hc.items():
        status = result.get('status', 'UNKNOWN')
        value = result.get('value', 'N/A')
        message = result.get('message', '')
        
        # Status emoji
        if status == 'PASS':
            emoji = '✓'
        elif status == 'WARN':
            emoji = '⚠'
        elif status == 'FAIL':
            emoji = '✗'
        elif status == 'EXCELLENT':
            emoji = '★'
        else:
            emoji = 'ℹ'
        
        print(f"  {emoji} [{status:8}] {check_name}: {value}")
        if message and status != 'PASS':
            print(f"              └─ {message}")
    
    print(f"\n  Summary: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL")
    
    # Step 4: Save scored CSV
    print("\n[4/5] Saving scored CSV...")
    csv_out = OUTPUT_DIR / (csv_path.stem + "_scored.csv")
    df.to_csv(csv_out, index=False, encoding='utf-8')
    print(f"  ✓ Saved: {csv_out.name}")
    
    # Step 5: Generate PDF
    print("\n[5/5] Generating Black Kit PDF (7 pages)...")
    
    # Extract market info
    market_name, quarter, year = extract_market_info(df)
    
    # Generate standardized filename
    pdf_filename = generate_aps_filename(market_name, quarter, year, "Core_Equity_Feed")
    pdf_out = OUTPUT_DIR / pdf_filename
    
    print(f"  → Market: {market_name}")
    print(f"  → Period: Q{quarter} {year}")
    print(f"  → Output: {pdf_filename}")
    
    render_pdf(df, pdf_out, csv_filename=csv_path.name, 
              market_name=market_name, quarter=quarter, year=year)
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE ✓")
    print("="*60)
    print(f"\n📊 Scored CSV: {csv_out}")
    print(f"📄 Black Kit PDF: {pdf_out}")
    print(f"\n🎨 Branding Applied:")
    print(f"   • True Black Background (RGB 0,0,0)")
    print(f"   • Teal Headers (#00D1D1)")
    print(f"   • White Text")
    print(f"   • Globe Logo + 'Clean Data You Can Trust'")
    print(f"   • 7-Page Standard Layout")
    print("\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python aps_pipeline.py <csv_file_path>")
        print("Example: python aps_pipeline.py input/test.csv")
        print("\nOr use: RUN_ME.bat\n")
        sys.exit(1)
    
    main(sys.argv[1])