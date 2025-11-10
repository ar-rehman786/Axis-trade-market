# aps_render.py - Main PDF Renderer with Black Kit (CORRECTED ORDER)
"""
APS Market Intelligence - PDF Generator
CORRECTED 7-Page Order:
1. Cover
2. Churn Layer (Predictive Framework)
3. Risk Tier Segmentation
4. Churn Prediction Matrix ← FIXED
5. QA Schema
6. Sample Data
7. Geo Heatmap
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate

from engine.aps_config import ASSETS_DIR, LOGO_FILE
from engine.aps_feed_config import detect_feed_type, get_feed_config
from engine.aps_black_kit import APS_COLORS, generate_aps_filename
from engine.aps_pages import (
    create_page1_cover,
    create_page2_churn_layer,
    create_page3_risk_tiers,
    create_page4_churn_matrix,  # NEW!
    create_page5_qa_schema,
    create_page6_sample_data,
    create_page7_geo_heatmap
)

def create_header_footer_with_background(canvas, doc, logo_path=None):
    """
    Draw black background + header + footer on every page
    This runs BEFORE content is drawn
    """
    # 1. Draw black background FIRST
    canvas.saveState()
    canvas.setFillColorRGB(0, 0, 0)  # True Black RGB(0,0,0)
    canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    canvas.restoreState()
    
    # 2. Draw header with logo
    canvas.saveState()
    
    # Add logo if exists
    if logo_path and Path(logo_path).exists():
        try:
            canvas.drawImage(
                str(logo_path),
                letter[0]/2 - 1*inch,
                letter[1] - 1.2*inch,
                width=2*inch,
                height=0.8*inch,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception as e:
            print(f"  ⚠ Logo load failed: {e}")
    
    # Add slogan below logo
    canvas.setFont('Helvetica', 10)
    canvas.setFillColor(colors.HexColor('#00D1D1'))  # Teal
    canvas.drawCentredString(
        letter[0] / 2,
        letter[1] - 1.4*inch,
        "Clean Data You Can Trust"
    )
    
    canvas.restoreState()
    
    # 3. Draw footer
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#9CA3AF'))  # Gray
    
    # Left: Powered by
    canvas.drawString(
        0.75*inch,
        0.5*inch,
        "Powered by Axis AI Intelligence™"
    )
    
    # Center: Generated timestamp
    canvas.drawCentredString(
        letter[0] / 2,
        0.5*inch,
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    
    # Right: Page number
    canvas.drawRightString(
        letter[0] - 0.75*inch,
        0.5*inch,
        f"Page {doc.page}"
    )
    
    canvas.restoreState()

def render_pdf(df, out_path, csv_filename=None, market_name="Raleigh, NC", quarter=4, year=2025):
    """
    Main PDF rendering function with APS Black Kit branding
    
    CORRECTED 7-Page Order:
    1. Cover → Summary metrics
    2. Churn Layer → Dual-model framework + narrative
    3. Risk Tier Segmentation → Strategic tier analysis
    4. Churn Prediction Matrix → Equity × Age heatmap
    5. QA Schema → Field descriptions
    6. Sample Data → Representative records
    7. Geo Heatmap → ZIP-level concentration
    
    Args:
        df: DataFrame with processed data
        out_path: Output PDF path
        csv_filename: Original CSV filename for feed detection
        market_name: Market name for cover page
        quarter: Quarter number
        year: Year
    """
    
    # Detect feed type
    feed_type = detect_feed_type(filename=csv_filename, data=df)
    feed_config = get_feed_config(feed_type)
    
    print(f"✓ Detected feed type: {feed_config['name']}")
    print(f"✓ Rendering CORRECTED 7-page APS Market Intelligence Report")
    print(f"✓ Page Order: Cover → Churn Layer → Risk Tiers → Matrix → QA → Sample → Geo")
    print(f"✓ Applying APS Black Kit branding (True Black + Teal)")
    
    # Find logo
    logo_path = ASSETS_DIR / LOGO_FILE
    if not logo_path.exists():
        logo_path = None
        print(f"  ⚠ Logo not found at {logo_path}, proceeding without logo")
    
    # Create document
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1.6*inch,
        bottomMargin=0.75*inch
    )
    
    # Build story (all content in CORRECT ORDER)
    story = []
    
    print("  → Rendering Page 1: Cover...")
    create_page1_cover(story, df, market_name, quarter, year)
    
    print("  → Rendering Page 2: Churn Layer (Predictive Framework)...")
    create_page2_churn_layer(story, df)
    
    print("  → Rendering Page 3: Risk Tier Segmentation...")
    create_page3_risk_tiers(story, df)
    
    print("  → Rendering Page 4: Churn Prediction Matrix (Heatmap)...")
    create_page4_churn_matrix(story, df)
    
    print("  → Rendering Page 5: QA Schema...")
    create_page5_qa_schema(story, df)
    
    print("  → Rendering Page 6: Sample Data...")
    create_page6_sample_data(story, df)
    
    print("  → Rendering Page 7: Geo Heatmap...")
    create_page7_geo_heatmap(story, df)
    
    # Create page template with background
    def page_builder(canvas, doc):
        create_header_footer_with_background(canvas, doc, logo_path)
    
    # Build PDF
    doc.build(story, 
             onFirstPage=page_builder,
             onLaterPages=page_builder)
    
    print(f"✓ PDF generated successfully: {out_path}")
    print(f"✓ Total pages: 7")
    print(f"✓ Page 4 now includes: Churn Prediction Matrix (Equity × Age Heatmap)")
    print(f"✓ Branding: APS Black Kit (True Black RGB 0,0,0)")
    print(f"✓ Feed Type: {feed_config['name']}")

# Test function
if __name__ == "__main__":
    print("Testing APS PDF Renderer with CORRECTED page order...")
    
    # Create test data
    test_data = {
        'Property Address': ['123 Main St'] * 10,
        'City': ['Raleigh'] * 10,
        'State': ['NC'] * 10,
        'ZIP': ['27601'] * 10,
        'EstValue': [350000] * 10,
        'TotalLoanBal': [250000] * 10,
        'LTV %': [71.4] * 10,
        'Equity %': [28.6] * 10,
        'Equity_Dollars': [99995] * 10,
        'Loan_Age_Mo': [57] * 10,
        'APS_Score (v2.0)': [42.1] * 10,
        'APS_Tier': ['Nurture'] * 10
    }
    
    df = pd.DataFrame(test_data)
    
    output_path = Path("test_black_kit_corrected.pdf")
    render_pdf(df, output_path, "test.csv")
    
    print(f"\n✓ Test PDF created: {output_path}")
    print("✓ Verify Page 4 now has Churn Prediction Matrix heatmap")