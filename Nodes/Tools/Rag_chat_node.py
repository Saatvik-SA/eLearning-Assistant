from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from Agents.Rag_chat import answer_question_rag

class RAGChatInput(BaseModel):
    query: str = Field(..., description="User's academic question.")
    collection: object = Field(..., description="ChromaDB collection of embedded context.")
    embedder: object = Field(..., description="Embedding model used for query encoding.")

@tool(args_schema=RAGChatInput)
def rag_chat_node(inputs: RAGChatInput) -> dict:
    """
    Answers an academic question using context retrieved via RAG from embedded documents.
    """
    print(f"[RAG Chat Node] Processing question: {inputs.query}")
    answer = answer_question_rag(inputs.query, inputs.embedder, inputs.collection)

    return {
        "status": "success",
        "answer": answer,
        "source": "retrieved from uploaded academic context"
    }
