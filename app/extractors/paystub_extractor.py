import re


def extract_money(label, text):
    pattern = rf"{label}[\s:]*\$?([\d,]+\.\d{{2}})"
    match = re.search(pattern, text, re.IGNORECASE)
    try:
        return match.group(1).replace(",", "")
    except:
        return None


def extract_text_after_label(label, text):
    pattern = rf"{label}[\s:]*([^\n]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    try:
        return match.group(1).strip()
    except:
        return None


def extract_paystub_fields(text):
    return {
        "employee_name": extract_text_after_label("employee", text),
        "employer_name": extract_text_after_label("employer", text),
        "gross_pay": extract_money("gross pay", text),
        "net_pay": extract_money("net pay", text),
    }