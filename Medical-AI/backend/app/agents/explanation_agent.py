from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:7b"
)


def explanation_agent(state):

    prompt = f"""
You are an experienced physician.

Explain this medical report.

Parsed Report:

{state.get("parsed_report", {})}

Medical Knowledge:

{state.get("context","")}

User Question:

{state.get("question","Explain my report")}

Instructions:

- Explain every abnormal value.
- Explain possible diseases.
- Explain what each test means.
- Mention if a doctor consultation is advised.
- Never invent values.
- If RAG context exists, use it.
"""

    response = llm.invoke(prompt)

    state["answer"] = response.content

    return state