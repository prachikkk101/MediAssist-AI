import chromadb


def get_chroma_client():

    client = chromadb.PersistentClient(
        path="chroma_db"
    )

    return client