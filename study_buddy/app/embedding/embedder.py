from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def embed_text(texts):
    """Embeds a list of text chunks."""
    return model.encode(texts, convert_to_numpy=True)
