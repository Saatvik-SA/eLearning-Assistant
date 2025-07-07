# --- Utilities/Embeddings.py ---
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def get_query_embedding(query: str):
    """Return embedding vector for a query."""
    return embedder.encode(query).tolist()

def get_chunk_embeddings(chunks: list[str]):
    """Return embeddings for a list of text chunks."""
    return embedder.encode(chunks, show_progress_bar=True)

def get_embedder():
    return embedder
