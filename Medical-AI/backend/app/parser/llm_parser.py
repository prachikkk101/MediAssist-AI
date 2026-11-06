import json
import re

from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
    num_ctx=4096,
)


def parse_medical_report(text: str):

    prompt = f"""
You are an expert medical document parser.

Extract all useful medical information.

Return ONLY valid JSON.

DO NOT use markdown.

DO NOT write ```json.

Output must begin with {{
and end with }}

Schema:

{{
    "patient": {{
        "name": "",
        "age": null,
        "sex": ""
    }},
    "vitals": {{
        "blood_pressure": "",
        "pulse": "",
        "weight": ""
    }},
    "laboratory": {{
        "fasting_blood_glucose": "",
        "hba1c": ""
    }},
    "diagnosis": [],
    "medications": [],
    "recommendations": []
}}

Medical Report:

{text}
"""

    response = llm.invoke(prompt)

    content = response.content.strip()

    print("\n========== RAW LLM OUTPUT ==========")
    print(content)
    print("====================================\n")

    # Extract JSON even if wrapped in markdown
    match = re.search(r"\{.*\}", content, re.DOTALL)

    if not match:
        print("[WARN] No JSON found.")
        return {}

    try:

        parsed = json.loads(match.group())

        return parsed

    except Exception as e:

        print("JSON Error:", e)

        return {}