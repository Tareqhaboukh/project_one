def parse_invoice_pdf(pdf_bytes):
    from PyPDF2 import PdfReader
    import io
    import re
    from datetime import datetime
    from models import Vendors

    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = {}

    # Try extracting AcroForm fields first
    form_data = reader.get_fields()
    if form_data:
        print("=== FORM FIELD NAMES AND VALUES ===")
        for key, val in form_data.items():
            value = val.get('/V')
            print(f"{key}: {value}")
            if value:
                fields[key.lower()] = str(value).strip()
        print("=== END ===")
    else:
        # Fallback: extract visible text if no form fields
        text = "".join([page.extract_text() or "" for page in reader.pages])
        fields['invoice_number'] = re.search(r"Invoice\s*Number[:\s]*([A-Za-z0-9-]+)", text, re.IGNORECASE)
        fields['date'] = re.search(r"Date[:\s\n]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})", text, re.IGNORECASE)
        fields['amount'] = re.search(r"Amount[:\s]*\$?\s*([0-9.,]+)", text, re.IGNORECASE)
        fields['tax'] = re.search(r"Tax[:\s]*\$?\s*([0-9.,]+)", text, re.IGNORECASE)
        fields['description'] = re.search(r"Description[:\s]*(.+)", text, re.IGNORECASE)
        fields['vendor_name'] = re.search(r"Vendor[:\s]*(.+)", text, re.IGNORECASE)

        for key, match in fields.items():
            fields[key] = match.group(1).strip() if match else None

    # Normalize and map expected names
    parsed = {
        'invoice_number': fields.get('invoice_number'),
        'date': fields.get('date'),
        'amount': fields.get('amount'),
        'tax': fields.get('tax'),
        'description': fields.get('description'),
        'vendor_name': fields.get('vendor') or fields.get('vendor_name'),
    }

    # Convert date to datetime.date
    if parsed['date']:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                dt = datetime.strptime(parsed['date'], fmt)
                parsed['date'] = dt.strftime("%m/%d/%Y")  # always return string
                break
            except ValueError:
                continue
        else:
            parsed['date'] = None

    # Convert numbers
    if parsed['amount']:
        try:
            parsed['amount'] = float(str(parsed['amount']).replace(",", ""))
        except ValueError:
            parsed['amount'] = None

    if parsed['tax']:
        try:
            parsed['tax'] = float(str(parsed['tax']).replace(",", ""))
        except ValueError:
            parsed['tax'] = None

    # Match vendor in DB
    vendor = None
    if parsed['vendor_name']:
        vendor = Vendors.query.filter(Vendors.vendor_name.ilike(f"%{parsed['vendor_name']}%")).first()

    parsed['vendor_id'] = vendor.id if vendor else None
    parsed['vendor_name'] = vendor.vendor_name if vendor else parsed['vendor_name']

    return parsed, None