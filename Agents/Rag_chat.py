# --- Agents/Rag_chat.py ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from Utilities.Embeddings import get_query_embedding
from Utilities.ChromaDB import query_chromadb_for_context

def answer_question_rag(query: str, embedder, collection) -> str:
    """
    Answers a single academic question using RAG from embedded documents.
    """
    query_embedding = get_query_embedding(query)
    context = query_chromadb_for_context(query_embedding)

    prompt = ChatPromptTemplate.from_template("""You are a helpful academic assistant.

Based only on the provided academic context, answer the user's query clearly and accurately.
Avoid hallucinating or guessing if the context does not support the answer.

--- CONTEXT ---
{context}

--- USER QUESTION ---
{query}
""")

    formatted = prompt.format_messages(context=context, query=query)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    response = llm.invoke(formatted)

    return response.content.strip()

def run_rag_chat(embedder, collection):
    """
    CLI loop for asking multiple questions interactively.
    """
    print("\nEnter your academic question (or type 'exit' to quit):")
    while True:
        query = input("Ask: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Exiting RAG chat.")
            break
        answer = answer_question_rag(query, embedder, collection)
        print("\nAnswer:", answer)
