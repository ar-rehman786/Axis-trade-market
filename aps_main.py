# # aps_main.py - APS Market Intelligence Pipeline
# """
# Complete pipeline integrating:
# - CSV processing
# - TypeScript metrics calculation
# - Data quality checks
# - Database storage
# - PDF generation
# - API integration
# """

# import pandas as pd
# import sys
# from pathlib import Path
# from datetime import datetime

# # Import APS modules
# # from aps_config import INPUT_DIR, OUTPUT_DIR, REQUIRED_HEADERS
# from engine.aps_config import INPUT_DIR, OUTPUT_DIR, REQUIRED_HEADERS
# from engine.aps_normalize import normalize_and_score
# from engine.aps_healthcheck import health_check
# from engine.aps_feed_config import detect_feed_type
# from engine.aps_render import render_pdf
# from engine.aps_database import MarketDataDB
# import engine.aps_metrics as metrics

# def print_banner():
#     """Print pipeline banner"""
#     print("=" * 60)
#     print("APS MARKET INTELLIGENCE PIPELINE")
#     print("=" * 60)

# def print_health_results(checks: dict):
#     """Print health check results in formatted table"""
#     print("-" * 60)
#     print("HEALTH CHECK RESULTS")
#     print("-" * 60)
    
#     for check_name, check_data in checks.items():
#         status = check_data.get('status', 'UNKNOWN')
#         value = check_data.get('value', 'N/A')
        
#         # Color-coded status
#         if status == 'PASS':
#             status_icon = '✓ [PASS    ]'
#         elif status == 'WARN':
#             status_icon = '⚠ [WARN    ]'
#         elif status == 'FAIL':
#             status_icon = '✗ [FAIL    ]'
#         elif status == 'EXCELLENT':
#             status_icon = '★ [EXCELLENT]'
#         else:
#             status_icon = '? [UNKNOWN ]'
        
#         # Format check name
#         check_display = check_name.replace('_', ' ').title()
        
#         print(f"  {status_icon} {check_name}: {value}")
        
#         # Print message if present
#         if 'message' in check_data:
#             message = check_data['message']
#             if len(message) < 50:
#                 print(f"              └─ {message}")
    
#     # Summary
#     pass_count = sum(1 for c in checks.values() if c.get('status') == 'PASS')
#     warn_count = sum(1 for c in checks.values() if c.get('status') == 'WARN')
#     fail_count = sum(1 for c in checks.values() if c.get('status') == 'FAIL')
    
#     print(f"  Summary: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL")

# def calculate_market_aggregates(df: pd.DataFrame) -> dict:
#     """
#     Calculate city/ZIP level aggregates for database storage
    
#     Args:
#         df: DataFrame with scored data
    
#     Returns:
#         Dictionary with city and ZIP aggregates
#     """
#     aggregates = {
#         'city': {},
#         'zips': []
#     }
    
#     # City-level summary
#     if 'City' in df.columns and 'State' in df.columns:
#         city = df['City'].mode()[0] if len(df) > 0 else 'Unknown'
#         state = df['State'].mode()[0] if len(df) > 0 else 'XX'
        
#         aggregates['city'] = {
#             'city': city,
#             'state': state,
#             'median_ltv': df['LTV %'].median() / 100 if 'LTV %' in df.columns else 0,
#             'median_equity_pct': df['Equity %'].median() / 100 if 'Equity %' in df.columns else 0,
#             'median_equity_dollars': df['Equity_Dollars'].median() if 'Equity_Dollars' in df.columns else 0,
#             'median_loan_age_months': int(df['Loan_Age_Mo'].median()) if 'Loan_Age_Mo' in df.columns else 0,
#             'refi_pressure': 74,  # Placeholder - calculate from refi-eligible percentage
#             'equity_delta_90d': 3.1,  # Placeholder - would come from historical data
#             'record_count': len(df)
#         }
    
#     # ZIP-level breakdowns
#     if 'ZIP' in df.columns:
#         zip_groups = df.groupby('ZIP')
        
#         for zip_code, group in zip_groups:
#             if len(group) < 5:  # Skip ZIPs with too few records
#                 continue
            
#             zip_data = {
#                 'zip': str(zip_code),
#                 'city': group['City'].mode()[0] if 'City' in group.columns else 'Unknown',
#                 'state': group['State'].mode()[0] if 'State' in group.columns else 'XX',
#                 'tip_zip_score': group['APS_Score (v2.0)'].median() if 'APS_Score (v2.0)' in group.columns else 0,
#                 'median_dom': 21,  # Placeholder - would come from transaction data
#                 'equity_delta_90d': 3.0,  # Placeholder
#                 'refi_pressure': 75,  # Placeholder
#                 'record_count': len(group),
#                 'median_ltv': group['LTV %'].median() / 100 if 'LTV %' in group.columns else 0,
#                 'median_equity_pct': group['Equity %'].median() / 100 if 'Equity %' in group.columns else 0,
#                 'median_equity_dollars': group['Equity_Dollars'].median() if 'Equity_Dollars' in group.columns else 0,
#                 'median_loan_age': int(group['Loan_Age_Mo'].median()) if 'Loan_Age_Mo' in group.columns else 0
#             }
            
#             aggregates['zips'].append(zip_data)
    
#     return aggregates

# def main(csv_path: Path):
#     """
#     Main pipeline execution
    
#     Args:
#         csv_path: Path to input CSV file
#     """
    
#     print_banner()
#     print(f"📁 Input file: {csv_path.name}")
    
#     # ===== STEP 1: Load CSV =====
#     print("[1/7] Loading CSV...")
#     try:
#         df = pd.read_csv(csv_path, encoding='utf-8-sig')
#         print(f"  ✓ Loaded {len(df)} records")
#         print(f"  ✓ Found {len(df.columns)} columns")
#     except Exception as e:
#         print(f"  ✗ Error loading CSV: {e}")
#         return
    
#     # ===== STEP 2: Normalize and Score =====
#     print("[2/7] Normalizing and scoring data...")
#     try:
#         df = normalize_and_score(df)
#         print(f"  ✓ Calculated LTV, Equity, Loan Age")
#         print(f"  ✓ Calculated APS Score v2.0")
#         print(f"  ✓ Assigned APS Tiers")
#         print(f"  ✓ Calculated CCI Index")
#     except Exception as e:
#         print(f"  ⚠ Scoring error: {e}")
    
#     # ===== STEP 3: Health Check =====
#     print("[3/7] Running 18-point health check...")
#     checks = health_check(df)
#     print_health_results(checks)
    
#     # ===== STEP 4: Save Scored CSV =====
#     print("[4/7] Saving scored CSV...")
#     scored_csv_name = csv_path.stem + "_scored.csv"
#     scored_csv_path = OUTPUT_DIR / scored_csv_name
#     try:
#         df.to_csv(scored_csv_path, index=False, encoding='utf-8-sig')
#         print(f"  ✓ Saved: {scored_csv_name}")
#     except Exception as e:
#         print(f"  ⚠ CSV save error: {e}")
    
#     # ===== STEP 5: Store in Database =====
#     print("[5/7] Storing aggregates in database...")
#     try:
#         db = MarketDataDB()
#         db.initialize()
        
#         # Calculate aggregates
#         aggregates = calculate_market_aggregates(df)
        
#         # Store city data
#         if aggregates['city']:
#             db.upsert_city_metrics(
#                 aggregates['city']['city'],
#                 aggregates['city']['state'],
#                 aggregates['city']
#             )
#             print(f"  ✓ Stored city data: {aggregates['city']['city']}, {aggregates['city']['state']}")
        
#         # Store ZIP data
#         for zip_data in aggregates['zips'][:10]:  # Limit to top 10 ZIPs
#             db.upsert_zip_metrics(
#                 zip_data['zip'],
#                 zip_data['city'],
#                 zip_data['state'],
#                 zip_data
#             )
#         print(f"  ✓ Stored {min(10, len(aggregates['zips']))} ZIP breakdowns")
        
#         # Update pulse
#         median_equity_delta = 3.9  # Placeholder
#         median_refi_pressure = 74
#         active_markets = len(aggregates['zips'])
#         db.update_pulse(median_equity_delta, median_refi_pressure, active_markets)
#         print(f"  ✓ Updated market pulse")
        
#         db.close()
        
#     except Exception as e:
#         print(f"  ⚠ Database storage error: {e}")
    
#     # ===== STEP 6: Generate PDF =====
#     print("[6/7] Generating Black Kit PDF (7 pages)...")
    
#     # Determine market name and quarter
#     market_name = aggregates['city'].get('city', 'Unknown') if aggregates['city'] else 'Unknown'
#     quarter = (datetime.now().month - 1) // 3 + 1
#     year = datetime.now().year
    
#     pdf_name = f"APS_{market_name.replace(' ', '_')}_Q{quarter}_{year}_Core_Equity_Feed_BrandLocked.pdf"
#     pdf_path = OUTPUT_DIR / pdf_name
    
#     print(f"  → Market: {market_name}")
#     print(f"  → Period: Q{quarter} {year}")
#     print(f"  → Output: {pdf_name}")
    
#     try:
#         render_pdf(
#             df,
#             pdf_path,
#             csv_filename=csv_path.name,
#             market_name=market_name,
#             quarter=quarter,
#             year=year
#         )
#     except Exception as e:
#         print(f"  ⚠ PDF generation error: {e}")
    
#     # ===== STEP 7: Summary =====
#     print("[7/7] Pipeline complete!")
#     print("=" * 60)
#     print("PIPELINE COMPLETE ✓")
#     print("=" * 60)
#     print(f"📊 Scored CSV: {scored_csv_path}")
#     print(f"📄 Black Kit PDF: {pdf_path}")
#     print(f"🎨 Branding Applied:")
#     print(f"   • True Black Background (RGB 0,0,0)")
#     print(f"   • Teal Headers (#00D1D1)")
#     print(f"   • White Text")
#     print(f"   • Globe Logo + 'Clean Data You Can Trust'")
#     print(f"   • 7-Page Standard Layout")
#     print(f"\n💡 API Server available at: http://localhost:8080")
#     print(f"   Run: python aps_api.py to start backend")
#     print("=" * 60)

# if __name__ == "__main__":
#     # Get CSV file path
#     if len(sys.argv) > 1:
#         csv_file = Path(sys.argv[1])
#     else:
#         # Default to test.csv in input directory
#         csv_file = INPUT_DIR / "test.csv"
    
#     # Check if file exists
#     if not csv_file.exists():
#         print(f"❌ Error: File not found: {csv_file}")
#         print(f"\nUsage: python aps_main.py <csv_file>")
#         print(f"Example: python aps_main.py input/test.csv")
#         sys.exit(1)
    
#     # Run pipeline
#     main(csv_file)



# aps_main.py - APS Market Intelligence Pipeline
"""
Complete pipeline integrating:
- CSV processing
- TypeScript metrics calculation
- Data quality checks
- Database storage
- PDF generation
- API integration
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Import APS modules
from engine.aps_config import INPUT_DIR, OUTPUT_DIR, REQUIRED_HEADERS
from engine.aps_normalize import normalize_and_score
from engine.aps_healthcheck import health_check
from engine.aps_feed_config import detect_feed_type
from engine.aps_render import render_pdf
from engine.aps_database import MarketDataDB
import engine.aps_metrics as metrics

def print_banner():
    """Print pipeline banner"""
    print("=" * 60)
    print("APS MARKET INTELLIGENCE PIPELINE")
    print("=" * 60)

def print_health_results(checks: dict):
    """Print health check results in formatted table"""
    print("-" * 60)
    print("HEALTH CHECK RESULTS")
    print("-" * 60)
    
    for check_name, check_data in checks.items():
        status = check_data.get('status', 'UNKNOWN')
        value = check_data.get('value', 'N/A')
        
        # Color-coded status
        if status == 'PASS':
            status_icon = '✓ [PASS    ]'
        elif status == 'WARN':
            status_icon = '⚠ [WARN    ]'
        elif status == 'FAIL':
            status_icon = '✗ [FAIL    ]'
        elif status == 'EXCELLENT':
            status_icon = '★ [EXCELLENT]'
        else:
            status_icon = '? [UNKNOWN ]'
        
        # Format check name
        check_display = check_name.replace('_', ' ').title()
        
        print(f"  {status_icon} {check_name}: {value}")
        
        # Print message if present
        if 'message' in check_data:
            message = check_data['message']
            if len(message) < 50:
                print(f"              └─ {message}")
    
    # Summary
    pass_count = sum(1 for c in checks.values() if c.get('status') == 'PASS')
    warn_count = sum(1 for c in checks.values() if c.get('status') == 'WARN')
    fail_count = sum(1 for c in checks.values() if c.get('status') == 'FAIL')
    
    print(f"  Summary: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL")

def calculate_market_aggregates(df: pd.DataFrame) -> dict:
    """
    Calculate city/ZIP level aggregates for database storage
    
    Args:
        df: DataFrame with scored data
    
    Returns:
        Dictionary with city and ZIP aggregates
    """
    aggregates = {
        'city': {},
        'zips': []
    }
    
    # City-level summary
    if 'City' in df.columns and 'State' in df.columns:
        city = df['City'].mode()[0] if len(df) > 0 else 'Unknown'
        state = df['State'].mode()[0] if len(df) > 0 else 'XX'
        
        aggregates['city'] = {
            'city': city,
            'state': state,
            'median_ltv': df['LTV %'].median() / 100 if 'LTV %' in df.columns else 0,
            'median_equity_pct': df['Equity %'].median() / 100 if 'Equity %' in df.columns else 0,
            'median_equity_dollars': df['Equity_Dollars'].median() if 'Equity_Dollars' in df.columns else 0,
            'median_loan_age_months': int(df['Loan_Age_Mo'].median()) if 'Loan_Age_Mo' in df.columns else 0,
            'refi_pressure': 74,  # Placeholder - calculate from refi-eligible percentage
            'equity_delta_90d': 3.1,  # Placeholder - would come from historical data
            'record_count': len(df)
        }
    
    # ZIP-level breakdowns
    if 'ZIP' in df.columns:
        zip_groups = df.groupby('ZIP')
        
        for zip_code, group in zip_groups:
            if len(group) < 5:  # Skip ZIPs with too few records
                continue
            
            zip_data = {
                'zip': str(zip_code),
                'city': group['City'].mode()[0] if 'City' in group.columns else 'Unknown',
                'state': group['State'].mode()[0] if 'State' in group.columns else 'XX',
                'tip_zip_score': group['APS_Score (v2.0)'].median() if 'APS_Score (v2.0)' in group.columns else 0,
                'median_dom': 21,  # Placeholder - would come from transaction data
                'equity_delta_90d': 3.0,  # Placeholder
                'refi_pressure': 75,  # Placeholder
                'record_count': len(group),
                'median_ltv': group['LTV %'].median() / 100 if 'LTV %' in group.columns else 0,
                'median_equity_pct': group['Equity %'].median() / 100 if 'Equity %' in group.columns else 0,
                'median_equity_dollars': group['Equity_Dollars'].median() if 'Equity_Dollars' in group.columns else 0,
                'median_loan_age': int(group['Loan_Age_Mo'].median()) if 'Loan_Age_Mo' in group.columns else 0
            }
            
            aggregates['zips'].append(zip_data)
    
    return aggregates

def main(csv_path: Path):
    """
    Main pipeline execution
    
    Args:
        csv_path: Path to input CSV file
    """
    
    print_banner()
    print(f"📁 Input file: {csv_path.name}")
    
    # ===== STEP 1: Load CSV =====
    print("[1/7] Loading CSV...")
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"  ✓ Loaded {len(df)} records")
        print(f"  ✓ Found {len(df.columns)} columns")
    except Exception as e:
        print(f"  ✗ Error loading CSV: {e}")
        return
    
    # ===== STEP 2: Normalize and Score =====
    print("[2/7] Normalizing and scoring data...")
    try:
        df = normalize_and_score(df)
        print(f"  ✓ Calculated LTV, Equity, Loan Age")
        print(f"  ✓ Calculated APS Score v2.0")
        print(f"  ✓ Assigned APS Tiers")
        print(f"  ✓ Calculated CCI Index")
    except Exception as e:
        print(f"  ⚠ Scoring error: {e}")
    
    # ===== STEP 3: Health Check =====
    print("[3/7] Running 18-point health check...")
    checks = health_check(df)
    print_health_results(checks)
    
    # ===== STEP 4: Save Scored CSV =====
    print("[4/7] Saving scored CSV...")
    scored_csv_name = csv_path.stem + "_scored.csv"
    scored_csv_path = OUTPUT_DIR / scored_csv_name
    try:
        df.to_csv(scored_csv_path, index=False, encoding='utf-8-sig')
        print(f"  ✓ Saved: {scored_csv_name}")
    except Exception as e:
        print(f"  ⚠ CSV save error: {e}")
    
    # ===== STEP 5: Calculate Aggregates (BEFORE database) =====
    aggregates = calculate_market_aggregates(df)
    
    # ===== STEP 6: Store in Database =====
    print("[5/7] Storing aggregates in database...")
    try:
        db = MarketDataDB()
        db.initialize()
        
        # Store city data
        if aggregates['city']:
            db.upsert_city_metrics(
                aggregates['city']['city'],
                aggregates['city']['state'],
                aggregates['city']
            )
            print(f"  ✓ Stored city data: {aggregates['city']['city']}, {aggregates['city']['state']}")
        
        # Store ZIP data
        for zip_data in aggregates['zips'][:10]:  # Limit to top 10 ZIPs
            db.upsert_zip_metrics(
                zip_data['zip'],
                zip_data['city'],
                zip_data['state'],
                zip_data
            )
        print(f"  ✓ Stored {min(10, len(aggregates['zips']))} ZIP breakdowns")
        
        # Update pulse
        median_equity_delta = 3.9  # Placeholder
        median_refi_pressure = 74
        active_markets = len(aggregates['zips'])
        db.update_pulse(median_equity_delta, median_refi_pressure, active_markets)
        print(f"  ✓ Updated market pulse")
        
        db.close()
        
    except Exception as e:
        print(f"  ⚠ Database storage error: {e}")
        import traceback
        traceback.print_exc()
    
    # ===== STEP 7: Generate PDF =====
    print("[6/7] Generating Black Kit PDF (7 pages)...")
    
    # Determine market name and quarter
    market_name = aggregates['city'].get('city', 'Unknown') if aggregates.get('city') else 'Unknown'
    quarter = (datetime.now().month - 1) // 3 + 1
    year = datetime.now().year
    
    pdf_name = f"APS_{market_name.replace(' ', '_')}_Q{quarter}_{year}_Core_Equity_Feed_BrandLocked.pdf"
    pdf_path = OUTPUT_DIR / pdf_name
    
    print(f"  → Market: {market_name}")
    print(f"  → Period: Q{quarter} {year}")
    print(f"  → Output: {pdf_name}")
    
    try:
        render_pdf(
            df,
            pdf_path,
            csv_filename=csv_path.name,
            market_name=market_name,
            quarter=quarter,
            year=year
        )
    except Exception as e:
        print(f"  ⚠ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
    
    # ===== STEP 8: Summary =====
    print("[7/7] Pipeline complete!")
    print("=" * 60)
    print("PIPELINE COMPLETE ✓")
    print("=" * 60)
    print(f"📊 Scored CSV: {scored_csv_path}")
    print(f"📄 Black Kit PDF: {pdf_path}")
    print(f"🎨 Branding Applied:")
    print(f"   • True Black Background (RGB 0,0,0)")
    print(f"   • Teal Headers (#00D1D1)")
    print(f"   • White Text")
    print(f"   • Globe Logo + 'Clean Data You Can Trust'")
    print(f"   • 7-Page Standard Layout")
    print(f"\n💡 API Server:")
    print(f"   Start: py -m uvicorn engine.aps_api:app --reload --port 8080")
    print(f"   Access: http://localhost:8080")
    print(f"   Docs: http://localhost:8080/docs")
    print("=" * 60)

if __name__ == "__main__":
    # Get CSV file path
    if len(sys.argv) > 1:
        csv_file = Path(sys.argv[1])
    else:
        # Default to test.csv in input directory
        csv_file = INPUT_DIR / "test.csv"
    
    # Check if file exists
    if not csv_file.exists():
        print(f"❌ Error: File not found: {csv_file}")
        print(f"\nUsage: python aps_main.py <csv_file>")
        print(f"Example: python aps_main.py input/test.csv")
        sys.exit(1)
    
    # Run pipeline
    main(csv_file)