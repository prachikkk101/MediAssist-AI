from langchain_chroma import Chroma

from app.rag.embeddings import get_embedding_model


PERSIST_DIRECTORY = "app/vector_db"


def get_retriever():

    embedding = get_embedding_model()

    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embedding,
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 4
        }
    )

    return retriever