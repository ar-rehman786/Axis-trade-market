# test_simple_pdf.py - Simple PDF Test to verify Black Kit styling
"""
Quick test to verify:
1. Black background renders
2. White/Teal text is visible
3. Tables display correctly
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def draw_background(canvas, doc):
    """Draw black background on every page"""
    canvas.saveState()
    canvas.setFillColorRGB(0, 0, 0)  # True Black
    canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    
    # Add header text
    canvas.setFont('Helvetica-Bold', 16)
    canvas.setFillColor(colors.HexColor('#00D1D1'))  # Teal
    canvas.drawCentredString(letter[0]/2, letter[1] - 1*inch, "APS BLACK KIT TEST")
    
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#9CA3AF'))  # Gray
    canvas.drawCentredString(letter[0]/2, 0.5*inch, f"Page {doc.page}")
    
    canvas.restoreState()

def create_test_pdf(filename="test_black_kit_simple.pdf"):
    """Create simple test PDF"""
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1.5*inch,
        bottomMargin=1*inch
    )
    
    story = []
    
    # Test 1: Teal Title
    title_style = ParagraphStyle(
        'TestTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#00D1D1'),  # Teal
        alignment=TA_CENTER,
        spaceAfter=20
    )
    story.append(Paragraph("Test Page 1: Teal Title", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Test 2: White Body Text
    body_style = ParagraphStyle(
        'TestBody',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.white,  # White
        spaceAfter=15
    )
    story.append(Paragraph("This is white body text. It should be clearly visible on black background.", body_style))
    story.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. This text should be readable.", body_style))
    
    # Test 3: Table with Teal Header and White Body
    table_data = [
        ['Column 1', 'Column 2', 'Column 3'],
        ['Data 1', 'Data 2', 'Data 3'],
        ['Data 4', 'Data 5', 'Data 6'],
        ['Data 7', 'Data 8', 'Data 9']
    ]
    
    t = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch])
    t.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D1D1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        
        # Body
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#404040')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.HexColor('#1A1A1A'),
            colors.HexColor('#0A0A0A')
        ]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(t)
    
    # Test 4: Yellow Highlight
    highlight_style = ParagraphStyle(
        'TestHighlight',
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#FFD166'),  # Yellow
        spaceAfter=15
    )
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("This is yellow highlighted text for emphasis.", highlight_style))
    
    # Page 2
    story.append(PageBreak())
    story.append(Paragraph("Test Page 2: Second Page Test", title_style))
    story.append(Paragraph("This text is on the second page. Background should still be black.", body_style))
    
    # Build PDF
    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)
    
    print(f"✓ Test PDF created: {filename}")
    print("  → Check if:")
    print("     1. Background is black on all pages")
    print("     2. Teal titles are visible")
    print("     3. White body text is readable")
    print("     4. Table has teal header with white body text")
    print("     5. Yellow text is visible")

if __name__ == "__main__":
    create_test_pdf()
    print("\n✓ Open 'test_black_kit_simple.pdf' to verify styling")