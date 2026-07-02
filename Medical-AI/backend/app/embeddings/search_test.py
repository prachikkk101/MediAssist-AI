from app.embeddings.model import get_embedding_model
import numpy as np


embedding_model = get_embedding_model()


documents = [
    "Hemoglobin is a protein in red blood cells",
    "Diabetes affects blood glucose levels",
    "Platelets help blood clotting",
    "Iron deficiency can reduce hemoglobin"
]


query = "Why is hemoglobin low?"


doc_vectors = [
    embedding_model.embed_query(doc)
    for doc in documents
]


query_vector = embedding_model.embed_query(query)


def cosine_similarity(a,b):

    return np.dot(a,b) / (
        np.linalg.norm(a)
        *
        np.linalg.norm(b)
    )


scores=[]


for doc,vector in zip(documents,doc_vectors):

    score = cosine_similarity(
        query_vector,
        vector
    )

    scores.append(
        (doc,score)
    )


scores.sort(
    key=lambda x:x[1],
    reverse=True
)


for doc,score in scores:

    print("\n")
    print(doc)
    print("Score:",score)