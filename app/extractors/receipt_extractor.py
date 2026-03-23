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


def extract_time(text):
    pattern = r"\b\d{1,2}:\d{2}(\s?[APMapm]{2})?\b"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None


def extract_merchant_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        return lines[0]
    return None


def extract_receipt_fields(text):
    return {
        "merchant_name": extract_merchant_name(text),
        "date": extract_date(text),
        "time": extract_time(text),
        "subtotal": extract_money("subtotal", text),
        "tax": extract_money("tax|hst|gst|vat", text),
        "tip": extract_money("tip|gratuity", text),
        "total": extract_money("total", text),
    }