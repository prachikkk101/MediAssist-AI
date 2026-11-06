from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:3b", temperature=0, num_ctx=4096)

MAX_REPORT_CHARS = 4000

FALLBACK = (
    "This report doesn't contain findings that call for specific dietary changes. "
    "General healthy-living tips (not based on this report):\n"
    "1. Maintain a balanced diet rich in fruits, vegetables, whole grains, and lean proteins.\n"
    "2. Stay hydrated by drinking plenty of water throughout the day.\n"
    "3. Focus on portion control and minimize heavily processed foods and added sugars."
)


def nutrition_agent(state):
    report_text = (state.get("report_text") or "").strip()[:MAX_REPORT_CHARS]
    parsed = {} if report_text else (state.get("parsed_report") or {})

    if not report_text and not parsed:
        state["nutrition"] = FALLBACK
        return state

    prompt = f"""You are a medical nutrition assistant.

RULES
- Base recommendations ONLY on conditions or findings that appear in the document.
- Never invent conditions, deficiencies or lab values.
- If nothing in the document relates to diet, say so in one sentence, then write "General healthy-living tips (not based on this report):" followed by at most 3 tips about food and hydration only.
- Do not prescribe medicines or supplements.

REPORT TEXT:
{report_text}

PARSED FIELDS (may be incomplete):
{parsed}

Format:
**Foods to include**
**Foods to limit**
**Lifestyle tips**
(Use "Not applicable" for any section that has nothing relevant.)
"""

    try:
        text = (llm.invoke(prompt).content or "").strip()
    except Exception as e:
        print(f"[NUTRITION] Error: {e}")
        text = ""

    nutrition_text = text or FALLBACK
    state["nutrition"] = nutrition_text

    # Only use the nutrition text as the chat answer for a nutrition question.
    # In full analysis it must not overwrite the explanation.
    if state.get("route") != "full_analysis":
        state["answer"] = nutrition_text

    return state