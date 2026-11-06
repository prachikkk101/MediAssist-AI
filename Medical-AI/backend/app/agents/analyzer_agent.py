from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:3b", temperature=0, num_ctx=4096)

MAX_REPORT_CHARS = 6000


def analyzer_agent(state):
    report_text = (state.get("report_text") or "").strip()[:MAX_REPORT_CHARS]
    parsed = state.get("parsed_report") or {}

    if not report_text and not parsed:
        state["analysis"] = "UNREADABLE"
        return state

    prompt = f"""You are analysing a medical document.

RULES
- Use ONLY information in REPORT TEXT or PARSED FIELDS.
- Never invent values, ranges, diagnoses or concerns.
- If REPORT TEXT and PARSED FIELDS disagree, trust REPORT TEXT.
- If the document has no numeric values (for example a cytology report or a
  consultation note), write "Not applicable" under the value sections.
- Only list a concern if the document itself states or clearly flags it.
- If the document is mostly unreadable, reply with exactly: UNREADABLE

REPORT TEXT:
{report_text}

PARSED FIELDS (may be incomplete):
{parsed}

Use exactly these headings:
**Abnormal values** (only those marked abnormal or outside the stated range)
**Normal values**
**Concerns stated in the document**
"""

    response = llm.invoke(prompt)
    state["analysis"] = (response.content or "").strip()
    return state