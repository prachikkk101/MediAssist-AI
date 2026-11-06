from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:3b", temperature=0, num_ctx=4096)

MAX_REPORT_CHARS = 4000


def summary_agent(state):
    explanation = (state.get("answer") or "").strip()
    report_text = (state.get("report_text") or "").strip()[:MAX_REPORT_CHARS]

    if explanation.upper() == "UNREADABLE" or not (explanation or report_text):
        state["summary"] = "UNREADABLE"
        return state

    prompt = f"""You are a medical assistant writing a short patient-friendly summary.

RULES
- Use ONLY facts found in REPORT TEXT or EXPLANATION below.
- Maximum 6 bullet points, simple language.
- Include: what kind of document this is, the main findings, and the doctor's
  advice only if stated.
- For conclusions, copy the document's impression wording. Do not rephrase it
  into extra reassurance such as "no signs of cancer".
- Do NOT add conditions, lifestyle advice, or tests that the document does not mention.
- Do NOT ask for more information.

REPORT TEXT:
{report_text}

EXPLANATION:
{explanation}
"""

    response = llm.invoke(prompt)
    state["summary"] = (response.content or "").strip()
    return state