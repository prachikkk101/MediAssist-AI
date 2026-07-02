from app.embeddings.model import get_embedding_model


embedding_model = get_embedding_model()


text = "Hemoglobin is low"

vector = embedding_model.embed_query(text)


print("Vector length:")
print(len(vector))


print("\nFirst 10 values:")
print(vector[:10])