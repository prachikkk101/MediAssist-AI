from app.rag.embeddings import get_embedding_model

embedding = get_embedding_model()

vector = embedding.embed_query("What is Hemoglobin?")

print(len(vector))