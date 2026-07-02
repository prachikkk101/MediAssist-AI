from app.embeddings.model import get_embedding_model
from app.vectorstore.chroma_store import get_chroma_client


print("Starting document insertion...")


embedding_model = get_embedding_model()

client = get_chroma_client()


collection = client.get_or_create_collection(
    name="medical_docs"
)


documents = [
    "Hemoglobin is a protein in red blood cells that carries oxygen.",
    "Low hemoglobin indicates anemia.",
    "Diabetes affects blood glucose regulation.",
    "Platelets help in blood clotting.",
    "Iron deficiency is a common cause of anemia."
]


embeddings = embedding_model.embed_documents(
    documents
)


collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=[
        f"doc_{i}"
        for i in range(len(documents))
    ]
)


print("Documents added successfully!")

print(
    "Total documents:",
    collection.count()
)