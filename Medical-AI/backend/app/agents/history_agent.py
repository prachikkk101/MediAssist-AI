
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
    num_ctx=4096,
)


def history_agent(state):
    print("\n========== HISTORY AGENT ==========")

    previous_report = state.get(
        "previous_report",
        ""
    )

    current_report = state.get(
        "parsed_report",
        {}
    )

    if not previous_report:
        state["history"] = (
            "No previous report was provided. "
            "A comparison cannot be performed."
        )
        return state

    if not current_report:
        state["history"] = (
            "The current report could not be parsed. "
            "Please check the report before comparing."
        )
        return state

    prompt = f"""
You are a careful medical report comparison assistant.

Compare the previous report with the current report.

PREVIOUS REPORT:
{previous_report}

CURRENT PARSED REPORT:
{current_report}

CURRENT EXPLANATION:
{state.get("answer", "")}

Instructions:

1. Compare matching laboratory tests only.
2. Report previous and current values accurately.
3. Calculate absolute numerical changes when possible.
4. Categorize changes as increased, decreased, or unchanged.
5. Do not automatically describe an increase or decrease
   as an improvement or deterioration.
6. Interpret clinical significance only when supported
   by units, reference ranges, and appropriate context.
7. Do not diagnose diseases from changes alone.
8. Do not invent missing values, units, dates, or ranges.
9. If units or reference ranges are unavailable, say so.
10. If a test appears in only one report, mention that
    it cannot be compared.
11. Use clear, patient-friendly language.
12. Recommend discussing clinically important changes
    with a qualified healthcare professional.

Format:

### Report Comparison
### Changes in Each Test
### Overall Interpretation
### Recommended Follow-up

Do not claim a value is normal or abnormal without
sufficient reference information.
"""

    try:
        response = llm.invoke(prompt)
        state["history"] = response.content
        print("[OK] History comparison completed.")

    except Exception as e:
        print(f"[ERROR] History Agent Error: {e}")
        state["history"] = (
            "Unable to compare the reports. "
            "Please try again."
        )

    return state
