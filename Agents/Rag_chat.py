from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

def run_rag_chat(embedder, collection):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    prompt = ChatPromptTemplate.from_template("""
You are a helpful academic assistant. You must answer clearly and accurately using only the context provided.

If the context does not contain the answer, say: "I could not find a reliable answer based on the material provided."

---
Context:
{context}

Question:
{question}
""")

    query = input("Enter your question: ")
    query_embedding = embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    retrieved_chunks = results["documents"][0]
    context = "\n\n".join(retrieved_chunks)

    formatted_prompt = prompt.format_messages(
        context=context,
        question=query
    )

    response = llm.invoke(formatted_prompt)

    print("\nYour Answer:\n")
    print(response.content)
