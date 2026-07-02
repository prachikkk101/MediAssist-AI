import os
import shutil

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma

from app.rag.embeddings import get_embedding_model


KNOWLEDGE_DIR = "app/knowledge"
VECTOR_DB_DIR = "app/vector_db"


def load_documents():

    documents = []

    for root, _, files in os.walk(KNOWLEDGE_DIR):

        for file in files:

            if file.endswith(".txt"):

                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:

                    text = f.read()

                documents.append(

                    Document(

                        page_content=text,

                        metadata={

                            "source": file

                        }

                    )

                )

    return documents


def build_vector_db():

    print("=" * 60)
    print("Loading documents...")
    print("=" * 60)

    docs = load_documents()

    print(f"Loaded {len(docs)} document(s).")

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=800,

        chunk_overlap=150

    )

    chunks = splitter.split_documents(docs)

    print(f"Created {len(chunks)} chunks.")

    embedding = get_embedding_model()

    if os.path.exists(VECTOR_DB_DIR):

        shutil.rmtree(VECTOR_DB_DIR)

    Chroma.from_documents(

        documents=chunks,

        embedding=embedding,

        persist_directory=VECTOR_DB_DIR

    )

    print("\nVector database created successfully!")
    print(f"Saved to: {VECTOR_DB_DIR}")


if __name__ == "__main__":

    build_vector_db()