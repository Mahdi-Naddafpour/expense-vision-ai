from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


def clean_ai_response(response_text: str):
    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


def ai_extract(text: str):
    prompt = f"""
Extract structured data from this document.

Return ONLY valid JSON.
Do not include markdown fences.
Do not include explanations.

Use this exact JSON structure:

{{
  "document_type": "receipt | invoice | paystub | cheque | other",
  "vendor_name": "",
  "document_date": "",
  "total_amount": "",
  "invoice_details": {{
    "company_name": "",
    "invoice_number": "",
    "date": "",
    "invoice_total": ""
  }},
  "transaction": {{
    "date": ""
  }},
  "pay_period": {{
    "cheque_date": ""
  }},
  "net_pay": {{
    "current": ""
  }},
  "employee": {{
    "name": ""
  }},
  "company": {{
    "name": ""
  }}
}}

Rules:
- Always include all keys, even if empty.
- total_amount must be the main final amount found in the document.
- document_date should be the main date of the document.
- If receipt, also fill transaction.date if possible.
- If invoice, also fill invoice_details.date and invoice_details.invoice_total if possible.
- If paystub, also fill pay_period.cheque_date and net_pay.current if possible.

Text:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        content = response.choices[0].message.content
        cleaned = clean_ai_response(content)
        return cleaned

    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response.choices[0].message.content if "response" in locals() else None
        }