from app.rag.retriever import get_retriever

retriever = get_retriever()

docs = retriever.invoke("What is hemoglobin?")

print()

print("Retrieved Documents:", len(docs))

print()

for i, doc in enumerate(docs, start=1):
    print(f"Result {i}")
    print("-" * 60)
    print(doc.page_content[:500])
    print()