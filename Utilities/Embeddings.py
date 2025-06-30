# --- Utilities/Embeddings.py ---

from sentence_transformers import SentenceTransformer

# Load SentenceTransformer model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Function to generate embedding for a single query (used in RAG QA)
def get_query_embedding(query: str):
    return embedder.encode(query).tolist()

# Function to generate embeddings for chunks (used in planner/quiz/etc.)
def get_chunk_embeddings(chunks: list[str]):
    return embedder.encode(chunks, show_progress_bar=True)

def get_embedder():
    return embedder
