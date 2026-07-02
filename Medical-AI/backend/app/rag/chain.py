from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.rag.retriever import get_retriever


llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0,
)


prompt = ChatPromptTemplate.from_template(
    """
You are an expert medical assistant.

Answer ONLY using the provided medical context.

If the answer is not present in the context, reply:

"I don't know based on the provided medical documents."

Context:
{context}

Question:
{question}
"""
)


def ask_question(question: str):

    retriever = get_retriever()

    docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    return response.content