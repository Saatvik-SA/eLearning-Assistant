# --- Utilities/ChromaDB.py ---
import chromadb
from chromadb.config import Settings

# Global collection for session
client = chromadb.Client(Settings())
collection = client.create_collection(name="pdf_chunks")

def add_chunks_to_chromadb(chunks, chunk_embeddings):
    """Add embedded chunks to ChromaDB collection."""
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"chunk_{i}"],
            embeddings=[chunk_embeddings[i]],
            metadatas=[{"source": f"pdf_chunk_{i}"}]
        )
    print("All chunks stored in ChromaDB.")

def query_chromadb_for_context(query_embedding, k=5):
    """Retrieve top-k most relevant chunks from ChromaDB for a given query embedding."""
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return "\n\n".join(results["documents"][0])

def get_all_chromadb_chunks():
    """Return all chunks stored in ChromaDB as a list of strings."""
    return collection.get(include=["documents"])['documents']

def get_chromadb_collection():
    """Return the ChromaDB collection object for advanced operations."""
    return collection
