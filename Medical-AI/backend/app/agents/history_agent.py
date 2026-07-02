from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5:7b"
)



def history_agent(state):

    prompt = f"""

You are a medical report comparison assistant.

Compare previous and current medical reports.

Explain:

1. Improvements
2. Worsening values
3. Stable values

Use simple patient-friendly language.

Previous Report:

{state.get("previous_report", "No previous report available")}


Current Report:

{state.get("parsed_report", {})}


Current Explanation:

{state.get("answer", "")}

"""


    response = llm.invoke(prompt)


    state["history"] = response.content


    return state