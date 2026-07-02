def supervisor_agent(state):

    question = state.get("question", "").lower()


    if any(word in question for word in [
        "compare",
        "previous",
        "old report",
        "history"
    ]):

        state["route"] = "history"


    elif any(word in question for word in [
        "food",
        "diet",
        "nutrition",
        "meal",
        "eat",
        "plan"
    ]):

        state["route"] = "nutrition"


    elif "summary" in question:

        state["route"] = "summary"


    else:

        state["route"] = "explanation"



    print("ROUTE:", state["route"])


    return state