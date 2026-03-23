from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# load .env
load_dotenv()

# گرفتن API KEY از .env
api_key = os.getenv("OPENAI_API_KEY")
print("API KEY:", api_key)

client = OpenAI(api_key=api_key)


# 🔧 تمیز کردن خروجی AI
def clean_ai_response(response_text):
    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


def ai_extract(text: str):
    prompt = f"""
Extract structured data from this document.

Return ONLY valid JSON.

Detect document type: paystub, invoice, receipt, cheque, or other.

Extract all important fields you can find.

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

        # 🔥 اینجا باید داخل try باشه
        cleaned = clean_ai_response(content)

        return cleaned

    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response.choices[0].message.content if "response" in locals() else None
        }