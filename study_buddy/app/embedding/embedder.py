from sentence_transformers import SentenceTransformer
import numpy as np
import logging

# Initialize the model only once (use device='cpu' explicitly)
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

def embed_text(texts, batch_size=32):
    """
    Embeds a list of text chunks efficiently on CPU.

    Args:
        texts (List[str]): List of strings to embed.
        batch_size (int): Batch size for faster embedding on CPU.

    Returns:
        np.ndarray: Embeddings as a numpy array.
    """
    if not texts:
        return np.array([])

    try:
        return model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True  # Optional: speeds up cosine similarity
        )
    except Exception as e:
        logging.exception("Embedding failed")
        return np.array([])
