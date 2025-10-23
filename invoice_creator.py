from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

pdf_file = "standard_fillable_invoice.pdf"
width, height = A4
c = canvas.Canvas(pdf_file, pagesize=A4)

# ---------- Title ----------
title_text = "STANDARD INVOICE"
c.setFont("Helvetica-Bold", 24)
title_width = c.stringWidth(title_text, "Helvetica-Bold", 24)
c.setFillColor(colors.HexColor("#003366"))
c.drawString((width - title_width)/2, height - 80, title_text)

# Draw a horizontal line under title
c.setStrokeColor(colors.HexColor("#003366"))
c.setLineWidth(2)
c.line(40, height - 100, width - 40, height - 100)

# ---------- Field positions ----------
field_positions = {
    "Invoice Number": (50, height - 150),
    "Date": (50, height - 190),
    "Vendor": (50, height - 230),
    "Amount": (50, height - 270),
    "Tax": (50, height - 310),
    "Description": (50, height - 350)
}

c.setFont("Helvetica-Bold", 12)
form = c.acroForm

# Draw fields and horizontal separator lines
for label, (x, y) in field_positions.items():
    # Label
    c.setFillColor(colors.black)
    c.drawString(x, y + 5, f"{label}:")
    
    # Highlight rectangle (subtle background)
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.rect(x + 120, y, 300, 20, fill=True, stroke=False)
    
    # Fillable field
    form.textfield(
        name=label.replace(" ", "_"),
        x=x + 120, y=y,
        width=370, height=20,
        borderStyle='underlined',
        forceBorder=True,
        fillColor=colors.white
    )
    
    # Horizontal line below field
    # c.setStrokeColor(colors.grey)
    # c.setLineWidth(0.5)
    # c.line(x, y - 5, x + 430, y - 5)

# Bottom line for aesthetics
c.setStrokeColor(colors.grey)
c.setLineWidth(1)
c.line(40, y - 30, width - 40, y - 30)

c.save()
print(f"Enhanced fillable invoice generated: {pdf_file}")