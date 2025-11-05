# # aps_black_kit.py - APS Black Kit Corporate Styling
# """
# APS Market Intelligence - Black Kit Branding
# Corporate styling: True Black background, Teal accents, White text
# """

# from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle, PageBreak
# from reportlab.lib.styles import ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
# from pathlib import Path

# # ==================== APS BLACK KIT BRAND COLORS ====================
# APS_COLORS = {
#     'true_black': colors.HexColor('#000000'),      # RGB(0, 0, 0) - True Black
#     'teal': colors.HexColor('#00D1D1'),            # Primary Teal
#     'white': colors.whitesmoke,                     # White text
#     'yellow': colors.HexColor('#FFD166'),          # Accent Yellow
#     'red': colors.HexColor('#FF6B6B'),             # Alert Red
#     'gray': colors.HexColor('#9CA3AF')             # Subtle Gray
# }

# # ==================== HEADER WITH LOGO + SLOGAN ====================
# def create_aps_header(canvas, doc, logo_path=None):
#     """
#     Create APS-branded header with globe logo and slogan
#     "Clean Data You Can Trust"
#     """
#     canvas.saveState()
    
#     # Draw header background (optional - can be removed for clean look)
#     # canvas.setFillColor(APS_COLORS['true_black'])
#     # canvas.rect(0, letter[1] - 1.5*inch, letter[0], 1.5*inch, fill=True, stroke=False)
    
#     # Add logo if exists
#     if logo_path and Path(logo_path).exists():
#         try:
#             canvas.drawImage(
#                 str(logo_path),
#                 letter[0]/2 - 1*inch,  # Center horizontally
#                 letter[1] - 1.2*inch,   # Top position
#                 width=2*inch,
#                 height=0.8*inch,
#                 preserveAspectRatio=True,
#                 mask='auto'
#             )
#         except:
#             pass
    
#     # Add slogan below logo
#     canvas.setFont('Helvetica', 10)
#     canvas.setFillColor(APS_COLORS['teal'])
#     canvas.drawCentredString(
#         letter[0] / 2,
#         letter[1] - 1.4*inch,
#         "Clean Data You Can Trust"
#     )
    
#     canvas.restoreState()

# # ==================== FOOTER ====================
# def create_aps_footer(canvas, doc):
#     """
#     Create APS-branded footer with page number and powered by text
#     """
#     canvas.saveState()
    
#     canvas.setFont('Helvetica', 8)
#     canvas.setFillColor(APS_COLORS['gray'])
    
#     # Left: Powered by
#     canvas.drawString(
#         0.75*inch,
#         0.5*inch,
#         "Powered by Axis AI Intelligence™"
#     )
    
#     # Center: Generated timestamp
#     from datetime import datetime
#     canvas.drawCentredString(
#         letter[0] / 2,
#         0.5*inch,
#         f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
#     )
    
#     # Right: Page number
#     canvas.drawRightString(
#         letter[0] - 0.75*inch,
#         0.5*inch,
#         f"Page {doc.page}"
#     )
    
#     canvas.restoreState()

# # ==================== TEAL DIVIDER ====================
# def add_teal_divider(story):
#     """
#     Add teal horizontal divider line between sections
#     """
#     divider_table = Table([['']], colWidths=[7*inch])
#     divider_table.setStyle(TableStyle([
#         ('LINEABOVE', (0, 0), (-1, 0), 2, APS_COLORS['teal']),
#         ('TOPPADDING', (0, 0), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
#     ]))
#     story.append(divider_table)
#     story.append(Spacer(1, 0.2*inch))

# # ==================== BLACK KIT PAGE STYLES ====================
# def get_black_kit_styles():
#     """
#     Return ParagraphStyles for APS Black Kit branding
#     """
#     styles = {}
    
#     # Page Title (Teal, Large)
#     styles['PageTitle'] = ParagraphStyle(
#         'PageTitle',
#         fontName='Helvetica-Bold',
#         fontSize=20,
#         textColor=APS_COLORS['teal'],
#         spaceAfter=20,
#         alignment=TA_CENTER
#     )
    
#     # Section Header (Teal, Medium)
#     styles['SectionHeader'] = ParagraphStyle(
#         'SectionHeader',
#         fontName='Helvetica-Bold',
#         fontSize=16,
#         textColor=APS_COLORS['teal'],
#         spaceAfter=12,
#         spaceBefore=12
#     )
    
#     # Body Text (White)
#     styles['BodyWhite'] = ParagraphStyle(
#         'BodyWhite',
#         fontName='Helvetica',
#         fontSize=11,
#         textColor=APS_COLORS['white'],
#         spaceAfter=10,
#         leading=14
#     )
    
#     # Metric Value (Yellow accent)
#     styles['MetricValue'] = ParagraphStyle(
#         'MetricValue',
#         fontName='Helvetica-Bold',
#         fontSize=14,
#         textColor=APS_COLORS['yellow'],
#         alignment=TA_CENTER
#     )
    
#     # Alert Text (Red)
#     styles['AlertText'] = ParagraphStyle(
#         'AlertText',
#         fontName='Helvetica-Bold',
#         fontSize=12,
#         textColor=APS_COLORS['red'],
#         spaceAfter=10
#     )
    
#     # Insight Paragraph (White, Italic)
#     styles['InsightParagraph'] = ParagraphStyle(
#         'InsightParagraph',
#         fontName='Helvetica-Oblique',
#         fontSize=10,
#         textColor=APS_COLORS['white'],
#         spaceAfter=12,
#         leftIndent=20,
#         rightIndent=20,
#         leading=13
#     )
    
#     return styles

# # ==================== BLACK KIT TABLE STYLING ====================
# def get_black_kit_table_style(header_color='teal'):
#     """
#     Return TableStyle for Black Kit theme
#     """
#     color = APS_COLORS.get(header_color, APS_COLORS['teal'])
    
#     return TableStyle([
#         # Header row
#         ('BACKGROUND', (0, 0), (-1, 0), color),
#         ('TEXTCOLOR', (0, 0), (-1, 0), APS_COLORS['true_black']),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 11),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
#         # Body rows
#         ('TEXTCOLOR', (0, 1), (-1, -1), APS_COLORS['white']),
#         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 1), (-1, -1), 10),
        
#         # Grid
#         ('GRID', (0, 0), (-1, -1), 0.5, APS_COLORS['gray']),
#         ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
#             colors.HexColor('#1A1A1A'),  # Slightly lighter black
#             APS_COLORS['true_black']
#         ]),
        
#         # Padding
#         ('TOPPADDING', (0, 0), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
#         ('LEFTPADDING', (0, 0), (-1, -1), 10),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 10),
#     ])

# # ==================== HELPER FUNCTIONS ====================
# def create_black_background_image(width, height):
#     """
#     Create a black background rectangle for matplotlib plots
#     """
#     import matplotlib.pyplot as plt
#     import matplotlib.patches as patches
    
#     fig, ax = plt.subplots(figsize=(width, height), dpi=300)
#     fig.patch.set_facecolor('#000000')
#     ax.set_facecolor('#000000')
    
#     return fig, ax

# def apply_black_kit_to_plot(ax):
#     """
#     Apply Black Kit styling to matplotlib axis
#     """
#     ax.set_facecolor('#000000')
#     ax.tick_params(colors='#FFFFFF')
#     ax.spines['bottom'].set_color('#00D1D1')
#     ax.spines['left'].set_color('#00D1D1')
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.grid(True, alpha=0.15, color='#FFFFFF')
    
#     # Set label colors
#     ax.xaxis.label.set_color('#FFFFFF')
#     ax.yaxis.label.set_color('#FFFFFF')
#     ax.title.set_color('#00D1D1')

# # ==================== FILE NAMING CONVENTION ====================
# def generate_aps_filename(market, quarter, year, feed_type="Core_Equity_Feed"):
#     """
#     Generate standardized APS filename
#     Format: APS_[Market]_[Quarter_Year]_[FeedType]_BrandLocked.pdf
#     """
#     market_clean = market.replace(' ', '_').replace(',', '')
#     return f"APS_{market_clean}_Q{quarter}_{year}_{feed_type}_BrandLocked.pdf"

# # ==================== MAIN HEADER/FOOTER BUILDER ====================
# def build_with_black_kit(canvas, doc, logo_path=None):
#     """
#     Main function to build page with Black Kit branding
#     Combines header and footer
#     """
#     create_aps_header(canvas, doc, logo_path)
#     create_aps_footer(canvas, doc)




# aps_black_kit.py - APS Black Kit Corporate Styling
"""
APS Market Intelligence - Black Kit Branding
Corporate styling: True Black background, Teal accents, White text
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from pathlib import Path

# ==================== APS BLACK KIT BRAND COLORS ====================
APS_COLORS = {
    'true_black': colors.HexColor('#000000'),      # RGB(0, 0, 0) - True Black
    'teal': colors.HexColor('#00D1D1'),            # Primary Teal
    'white': colors.whitesmoke,                     # White text
    'yellow': colors.HexColor('#FFD166'),          # Accent Yellow
    'red': colors.HexColor('#FF6B6B'),             # Alert Red
    'gray': colors.HexColor('#9CA3AF')             # Subtle Gray
}

# ==================== HEADER WITH LOGO + SLOGAN ====================
def create_aps_header(canvas, doc, logo_path=None):
    """
    Create APS-branded header with globe logo and slogan
    "Clean Data You Can Trust"
    """
    canvas.saveState()
    
    # Draw header background (optional - can be removed for clean look)
    # canvas.setFillColor(APS_COLORS['true_black'])
    # canvas.rect(0, letter[1] - 1.5*inch, letter[0], 1.5*inch, fill=True, stroke=False)
    
    # Add logo if exists
    if logo_path and Path(logo_path).exists():
        try:
            canvas.drawImage(
                str(logo_path),
                letter[0]/2 - 1*inch,  # Center horizontally
                letter[1] - 1.2*inch,   # Top position
                width=2*inch,
                height=0.8*inch,
                preserveAspectRatio=True,
                mask='auto'
            )
        except:
            pass
    
    # Add slogan below logo
    canvas.setFont('Helvetica', 10)
    canvas.setFillColor(APS_COLORS['teal'])
    canvas.drawCentredString(
        letter[0] / 2,
        letter[1] - 1.4*inch,
        "Clean Data You Can Trust"
    )
    
    canvas.restoreState()

# ==================== FOOTER ====================
def create_aps_footer(canvas, doc):
    """
    Create APS-branded footer with page number and powered by text
    """
    canvas.saveState()
    
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(APS_COLORS['gray'])
    
    # Left: Powered by
    canvas.drawString(
        0.75*inch,
        0.5*inch,
        "Powered by Axis AI Intelligence™"
    )
    
    # Center: Generated timestamp
    from datetime import datetime
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

# ==================== TEAL DIVIDER ====================
def add_teal_divider(story):
    """
    Add teal horizontal divider line between sections
    """
    divider_table = Table([['']], colWidths=[7*inch])
    divider_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, APS_COLORS['teal']),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider_table)
    story.append(Spacer(1, 0.2*inch))

# ==================== BLACK KIT PAGE STYLES ====================
def get_black_kit_styles():
    """
    Return ParagraphStyles for APS Black Kit branding
    Fixed: All text colors explicitly set to white/teal for visibility
    """
    from reportlab.lib import colors as rl_colors
    
    styles = {}
    
    # Page Title (Teal, Large)
    styles['PageTitle'] = ParagraphStyle(
        'PageTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=rl_colors.HexColor('#00D1D1'),  # Teal
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Section Header (Teal, Medium)
    styles['SectionHeader'] = ParagraphStyle(
        'SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=rl_colors.HexColor('#00D1D1'),  # Teal
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Body Text (White) - CRITICAL FIX
    styles['BodyWhite'] = ParagraphStyle(
        'BodyWhite',
        fontName='Helvetica',
        fontSize=11,
        textColor=rl_colors.white,  # Explicit white
        spaceAfter=10,
        leading=14
    )
    
    # Metric Value (Yellow accent)
    styles['MetricValue'] = ParagraphStyle(
        'MetricValue',
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=rl_colors.HexColor('#FFD166'),  # Yellow
        alignment=TA_CENTER
    )
    
    # Alert Text (Red)
    styles['AlertText'] = ParagraphStyle(
        'AlertText',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=rl_colors.HexColor('#FF6B6B'),  # Red
        spaceAfter=10
    )
    
    # Insight Paragraph (White, Italic)
    styles['InsightParagraph'] = ParagraphStyle(
        'InsightParagraph',
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=rl_colors.white,  # White
        spaceAfter=12,
        leftIndent=20,
        rightIndent=20,
        leading=13
    )
    
    return styles

# ==================== BLACK KIT TABLE STYLING ====================
def get_black_kit_table_style(header_color='teal'):
    """
    Return TableStyle for Black Kit theme
    Fixed: Ensures white text on black background
    """
    color = APS_COLORS.get(header_color, APS_COLORS['teal'])
    
    return TableStyle([
        # Header row - Teal background with BLACK text (readable)
        ('BACKGROUND', (0, 0), (-1, 0), color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Black text on teal
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Body rows - WHITE text on dark background
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),  # WHITE text
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        
        # Grid - Light gray for visibility
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#404040')),  # Dark gray grid
        
        # Alternating row backgrounds (slightly lighter than pure black)
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.HexColor('#1A1A1A'),  # Slightly lighter black
            colors.HexColor('#0A0A0A')   # Very dark gray
        ]),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ])

# ==================== HELPER FUNCTIONS ====================
def create_black_background_image(width, height):
    """
    Create a black background rectangle for matplotlib plots
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    fig, ax = plt.subplots(figsize=(width, height), dpi=300)
    fig.patch.set_facecolor('#000000')
    ax.set_facecolor('#000000')
    
    return fig, ax

def apply_black_kit_to_plot(ax):
    """
    Apply Black Kit styling to matplotlib axis
    """
    ax.set_facecolor('#000000')
    ax.tick_params(colors='#FFFFFF')
    ax.spines['bottom'].set_color('#00D1D1')
    ax.spines['left'].set_color('#00D1D1')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.15, color='#FFFFFF')
    
    # Set label colors
    ax.xaxis.label.set_color('#FFFFFF')
    ax.yaxis.label.set_color('#FFFFFF')
    ax.title.set_color('#00D1D1')

# ==================== FILE NAMING CONVENTION ====================
def generate_aps_filename(market, quarter, year, feed_type="Core_Equity_Feed"):
    """
    Generate standardized APS filename
    Format: APS_[Market]_[Quarter_Year]_[FeedType]_BrandLocked.pdf
    """
    market_clean = market.replace(' ', '_').replace(',', '')
    return f"APS_{market_clean}_Q{quarter}_{year}_{feed_type}_BrandLocked.pdf"

# ==================== MAIN HEADER/FOOTER BUILDER ====================
def build_with_black_kit(canvas, doc, logo_path=None):
    """
    Main function to build page with Black Kit branding
    Combines header and footer
    """
    create_aps_header(canvas, doc, logo_path)
    create_aps_footer(canvas, doc)