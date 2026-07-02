from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5:7b"
)


def analyzer_agent(state):


    prompt=f"""

Analyze this medical report.

Find:

1. Abnormal values
2. Normal values
3. Possible concerns


Report:

{state.get("parsed_report")}

"""


    response=llm.invoke(prompt)


    state["analysis"]=response.content


    return state