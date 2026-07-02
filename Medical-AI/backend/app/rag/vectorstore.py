from langchain_chroma import Chroma

from app.rag.loader import load_documents
from app.rag.splitter import split_documents
from app.rag.embeddings import get_embedding_model


PERSIST_DIRECTORY = "app/vector_db"


def create_vector_store():

    print("Loading documents...")

    documents = load_documents()

    print(f"Loaded {len(documents)} documents")

    print("Splitting documents...")

    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    embedding = get_embedding_model()

    print("Creating Chroma Database...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=PERSIST_DIRECTORY,
    )

    print("Vector Database Created Successfully")

    return vectorstore