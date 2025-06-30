# --- Utilities/ChromaDB.py ---

import chromadb
from chromadb.config import Settings

# Initialize ChromaDB client and collection
client = chromadb.Client(Settings())
collection = client.create_collection(name="pdf_chunks")

# Function to add chunks and their embeddings to ChromaDB
def add_chunks_to_chromadb(chunks, chunk_embeddings):
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"chunk_{i}"],
            embeddings=[chunk_embeddings[i]],
            metadatas=[{"source": f"pdf_chunk_{i}"}]
        )
    print("All chunks stored in ChromaDB.")

# Function to get top-k similar documents from ChromaDB
def query_chromadb_for_context(query_embedding, k=5):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    retrieved_chunks = results["documents"][0]
    return "\n\n".join(retrieved_chunks)

# Function to retrieve all documents (e.g., for planning, quiz, etc.)
def get_all_chromadb_chunks():
    results = collection.get(include=["documents"])
    return results['documents']

def get_chromadb_collection():
    return collection

