from langchain_core.runnables import RunnableLambda
from Utilities.Core import prepare_academic_context

def context_resolver_node() -> RunnableLambda:
    """
    LangGraph node to resolve academic context by embedding uploaded or existing PDFs.

    Input:
    {
        "query": <str>,
        "uploaded_files": <list[str]>,
        "message": HumanMessage
    }

    Output:
    Adds academic embedding context:
    {
        "query": <str>,
        "revised_query": <str>,
        "uploaded_files": <list[str]>,
        "collection": <chromadb Collection>,
        "embedder": <SentenceTransformer>,
        "total_chunks": <int>
    }
    """
    def resolve_context(inputs: dict) -> dict:
        uploaded_files = inputs.get("uploaded_files", [])
        if uploaded_files:
            print(f"[Context Resolver] User uploaded files: {uploaded_files}")
        else:
            print("[Context Resolver] No uploaded files — using default context from Data/Upload.")

        collection, embedder, total_chunks = prepare_academic_context()

        return {
            **inputs,
            "collection": collection,
            "embedder": embedder,
            "total_chunks": total_chunks,
            "revised_query": inputs.get("query", "")  
        }

    return RunnableLambda(resolve_context)
