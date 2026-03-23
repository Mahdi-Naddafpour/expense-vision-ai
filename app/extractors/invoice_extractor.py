import re


def extract_money(label, text):
    pattern = rf"{label}[\s:]*\$?([\d,]+\.\d{{2}})"
    match = re.search(pattern, text, re.IGNORECASE)
    try:
        return match.group(1).replace(",", "")
    except:
        return None


def extract_date(text):
    patterns = [
        r"\b\d{4}[-/]\d{2}[-/]\d{2}\b",
        r"\b\d{2}[-/]\d{2}[-/]\d{4}\b",
        r"\b[a-zA-Z]{3,9}\s+\d{1,2},\s+\d{4}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_invoice_number(text):
    patterns = [
        r"invoice\s*(number|no|#)?[\s:]*([A-Z0-9\-]+)",
        r"inv[\s\-#:]*(\w+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        try:
            return match.group(match.lastindex)
        except:
            continue
    return None


def extract_vendor_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        return lines[0]
    return None


def extract_invoice_fields(text):
    return {
        "vendor_name": extract_vendor_name(text),
        "invoice_number": extract_invoice_number(text),
        "invoice_date": extract_date(text),
        "subtotal": extract_money("subtotal", text),
        "tax": extract_money("tax|hst|gst|vat", text),
        "discount": extract_money("discount", text),
        "total": extract_money("total|amount due|balance due", text),
    }