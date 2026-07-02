from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:7b"
)


def summary_agent(state):

    prompt = f"""
You are a medical assistant.

Create a short patient-friendly summary.

Medical Report:

{state.get("parsed_report", {})}

Explanation:

{state.get("answer","")}

Instructions:

- Maximum 6 bullet points
- Simple language
- Mention abnormal values
- Mention possible conditions
- Mention important lifestyle advice
- Do NOT ask for more information
"""

    response = llm.invoke(prompt)

    state["summary"] = response.content

    return state