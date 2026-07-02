from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding_model():

    embedding = HuggingFaceEmbeddings(

        model_name="sentence-transformers/all-MiniLM-L6-v2"

    )

    return embedding