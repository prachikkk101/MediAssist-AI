import re

# Match whole words only. Plain substring checks gave wrong routes:
# "plan" matches inside "ex-plan-ation" and "eat" matches inside "tr-eat-ment",
# so ordinary questions were being sent to the nutrition route.
HISTORY_PATTERN = re.compile(
    r"\b(compare|comparison|previous|previously|old report|history|earlier report)\b"
)

NUTRITION_PATTERN = re.compile(
    r"\b(food|foods|diet|diets|nutrition|nutritional|meal|meals|eat|eating|plan|"
    r"avoid|recipe|recipes)\b"
)

SUMMARY_PATTERN = re.compile(r"\b(summary|summarize|summarise|tl;?dr)\b")


def supervisor_agent(state):
    # The upload endpoint sets this to run the full pipeline
    # (explanation + summary + nutrition). Don't override it.
    if state.get("route") == "full_analysis":
        print("ROUTE: full_analysis")
        return state

    question = (state.get("question") or "").lower()

    if HISTORY_PATTERN.search(question):
        state["route"] = "history"

    elif NUTRITION_PATTERN.search(question):
        state["route"] = "nutrition"

    elif SUMMARY_PATTERN.search(question):
        state["route"] = "summary"

    else:
        state["route"] = "explanation"

    print("ROUTE:", state["route"])

    return state