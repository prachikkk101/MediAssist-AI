from app.rag.retriever import get_retriever

# Load retriever only once
retriever = get_retriever()


def rag_agent(state):
    """
    Retrieve relevant medical knowledge from the vector database.
    """

    print("\n========== RAG AGENT ==========")

    try:
        question = state.get("question", "")

        if not question:
            print("⚠ No question provided.")
            state["context"] = ""
            return state

        print(f"Question: {question}")

        # Retrieve relevant documents
        docs = retriever.invoke(question)

        print(f"✅ Retrieved {len(docs)} document(s).")

        context = ""

        for i, doc in enumerate(docs, start=1):
            print(f"\n----- Document {i} -----")
            print(doc.page_content[:200])  # Print first 200 characters
            context += doc.page_content
            context += "\n\n"

        state["context"] = context.strip()

        print("\n✅ Context prepared successfully.")

    except Exception as e:
        print(f"\n❌ RAG Agent Error: {e}")
        state["context"] = ""

    return state