from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

pdf_file = "structured_visual_invoice.pdf"
width, height = A4
c = canvas.Canvas(pdf_file, pagesize=A4)

# Title
c.setFont("Helvetica-Bold", 20)
c.drawString(220, height - 50, "INVOICE")

# Highlight boxes for fields
field_positions = {
    "Invoice Number": (50, height - 120),
    "Date": (50, height - 160),
    "Vendor": (50, height - 200),
    "Amount": (50, height - 240),
    "Tax": (50, height - 280),
    "Description": (50, height - 320)
}

c.setFont("Helvetica-Bold", 12)
form = c.acroForm

for label, (x, y) in field_positions.items():
    # Label
    c.setFillColor(colors.black)
    c.drawString(x, y + 5, f"{label}:")
    
    # Highlight rectangle (optional subtle color)
    c.setFillColor(colors.HexColor("#f0f0f0"))
    c.rect(x + 120, y, 300, 20, fill=True, stroke=False)
    
    # Fillable field
    form.textfield(name=label.replace(" ", "_"),
                   x=x + 120, y=y,
                   width=300, height=20,
                   borderStyle='underlined',
                   forceBorder=True,
                   fillColor=colors.white)

c.save()
print(f"Structured, visual fillable PDF generated: {pdf_file}")