from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:3b", temperature=0, num_ctx=4096)

MAX_REPORT_CHARS = 6000
DISCLAIMER = "*This is general information, not medical advice. Please consult your doctor.*"


def explanation_agent(state):
    report_text = (state.get("report_text") or "").strip()[:MAX_REPORT_CHARS]
    # Parsed fields are lossy; only use them when there is no raw text (chat follow-ups).
    parsed = {} if report_text else (state.get("parsed_report") or {})
    context = (state.get("context") or "").strip()
    question = state.get("question") or "Explain my report"

    if not report_text and not parsed:
        state["answer"] = "UNREADABLE"
        state["explanation"] = "UNREADABLE"
        return state

    prompt = f"""You are a careful medical assistant explaining a patient's document in plain language.

STRICT RULES
- Use ONLY information that appears in REPORT TEXT (or PARSED FIELDS if no report text is given).
- Copy names, IDs, dates, and hospital or lab names exactly as written.
  Never shorten, reorder, translate or guess them.
- Never invent or correct ages, sex, values, diagnoses or tests.
  If something is not stated, write "Not stated".
- The document may be a lab report, a doctor's consultation note, or a pathology
  or cytology report. Explain what it actually is. Do not treat every document
  like a blood test.
- In "What this means", restate only what the document says. Do not add
  reassurance or conclusions of your own such as "mostly normal" or
  "no signs of infection". Say what was or was not seen.
- If the document says something was "not seen" or "absent", include it.
- Under "Doctor's advice", write only advice, recommendations or follow-up that
  is written in the document. If there is none, write exactly: Not stated
- Do not suggest extra tests or conditions unless the document mentions them.
- Use REFERENCE MATERIAL only if it directly concerns a condition or test named in
  the document. Otherwise ignore it completely and do not mention it.
- Do not add any disclaimer; it is added automatically.
- If the document is mostly unreadable or meaningless, reply with exactly: UNREADABLE

REPORT TEXT:
{report_text}

PARSED FIELDS (only used when there is no report text):
{parsed}

REFERENCE MATERIAL (may be irrelevant):
{context}

USER QUESTION: {question}

Answer using exactly these headings, with no notes in brackets:
**Document type**
**Patient and report details** (name, age, sex, dates, referring doctor, hospital or lab, case number; only what is present)
**Key findings**
**What this means**
**Doctor's advice**
"""

    response = llm.invoke(prompt)
    text = (response.content or "").strip()

    if text.upper() != "UNREADABLE":
        text = f"{text}\n\n{DISCLAIMER}"

    state["answer"] = text
    state["explanation"] = text
    return state