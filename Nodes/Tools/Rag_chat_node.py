from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from Agents.Rag_chat import answer_question_rag

class RAGChatInput(BaseModel):
    query: str = Field(..., description="User's academic question.")
    collection: object = Field(..., description="ChromaDB collection of embedded context.")
    embedder: object = Field(..., description="Embedding model used for query encoding.")

def rag_chat_node(state: dict) -> dict:
    """
    Answers an academic question using context retrieved via RAG from embedded documents.
    Expects:
        state['query']: user's academic question
        state['collection']: ChromaDB collection
        state['embedder']: embedding model
    Mutates and returns state with answer.
    """
    from Agents.Rag_chat import answer_question_rag
    query = state.get("query")
    collection = state.get("collection")
    embedder = state.get("embedder")
    if not query or not collection or not embedder:
        state["status"] = "error"
        state["error"] = "Missing query, collection, or embedder for RAG chat."
        return state
    print(f"[RAG Chat Node] Processing question: {query}")
    answer = answer_question_rag(query, embedder, collection)
    state["status"] = "success"
    state["answer"] = answer
    state["response"] = answer
    state["summary"] = answer
    state["output_type"] = "text"
    state["source"] = "retrieved from uploaded academic context"
    return state

def rag_chat_node_wrapper():
    def node(state: dict) -> dict:
        return rag_chat_node(state)
    return node
