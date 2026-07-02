from langchain_ollama import ChatOllama


# Load LLM once
llm = ChatOllama(
    model="qwen2.5:7b"
)


def safety_agent(state):
    """
    Reviews the AI-generated medical explanation for safety.

    Checks for:
    - Dangerous advice
    - Incorrect diagnosis claims
    - Missing emergency warnings
    - Adds a medical disclaimer
    """

    print("\n========== SAFETY AGENT ==========")

    try:

        answer = state.get("answer", "")

        if not answer:
            print("⚠ No answer found to review.")
            state["safe_answer"] = ""
            return state

        prompt = f"""
You are an experienced medical safety reviewer.

Review the following AI-generated medical explanation.

Your tasks:

1. Detect dangerous or unsafe advice.
2. Remove any direct diagnosis.
3. Identify emergency symptoms if present.
4. Mention when the patient should consult a doctor.
5. Add a medical disclaimer.

Medical Explanation:

{answer}

Return a patient-friendly reviewed version.
"""

        print("Reviewing AI response...")

        response = llm.invoke(prompt)

        state["safe_answer"] = response.content

        print("✅ Safety review completed.")

    except Exception as e:
        print(f"❌ Safety Agent Error: {e}")
        state["safe_answer"] = ""

    return state