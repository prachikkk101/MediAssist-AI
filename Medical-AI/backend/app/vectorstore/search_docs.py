from app.embeddings.model import get_embedding_model
from app.vectorstore.chroma_store import get_chroma_client


embedding_model = get_embedding_model()

client = get_chroma_client()


collection = client.get_or_create_collection(
    name="medical_docs"
)


def search(query):

    query_embedding = embedding_model.embed_query(
        query
    )


    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=3
    )


    return results["documents"][0]



if __name__ == "__main__":

    question = "Why is hemoglobin low?"

    answers = search(question)


    print("\nTop Results:\n")


    for answer in answers:
        print("-", answer)