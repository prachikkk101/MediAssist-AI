from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5:7b"
)


def nutrition_agent(state):

    print("========== NUTRITION AGENT RUNNING ==========")


    prompt = f"""

You are a medical nutrition assistant.

Generate dietary recommendations based on this report.

Report:

{state.get("parsed_report", {})}

Provide:

- Foods to eat
- Foods to avoid
- Lifestyle tips

Do not prescribe medicines.

"""


    response = llm.invoke(prompt)


    nutrition_text = response.content


    print(nutrition_text)


    # IMPORTANT
    state["nutrition"] = nutrition_text

    # if frontend expects answer
    state["answer"] = nutrition_text


    return state