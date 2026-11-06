from app.rag.retriever import get_retriever

retriever = get_retriever()

MIN_REPORT_CHARS = 80
MAX_QUERY_CHARS = 1000
MAX_CONTEXT_CHARS = 3000
GENERIC_QUESTIONS = {"", "explain my report", "explain this report", "summarize my report"}


def rag_agent(state):
    """Retrieve reference material based on what the report actually says."""
    state["context"] = ""

    report_text = (state.get("report_text") or "").strip()
    question = (state.get("question") or "").strip()

    # Nothing real to look up: don't pull in random guideline text.
    if len(report_text) < MIN_REPORT_CHARS:
        print("[RAG] Skipped: report text too short")
        return state

    try:
        if question.lower() in GENERIC_QUESTIONS:
            query = report_text[:MAX_QUERY_CHARS]
        else:
            query = f"{question}\n{report_text[:MAX_QUERY_CHARS - 200]}"

        docs = retriever.invoke(query)
        print(f"[RAG] Retrieved {len(docs)} document(s)")

        seen, parts, total = set(), [], 0
        for doc in docs:
            content = doc.page_content.strip()
            if not content or content in seen:
                continue
            if total + len(content) > MAX_CONTEXT_CHARS:
                break
            seen.add(content)
            parts.append(content)
            total += len(content)

        state["context"] = "\n\n".join(parts)

    except Exception as e:
        print(f"[RAG] Error: {e}")
        state["context"] = ""

    return state