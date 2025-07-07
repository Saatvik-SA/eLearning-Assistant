# --- Agents/Rescue_agent.py ---

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF
import os

def run_rescue_agent(collection, total_chunks, filename="Data/Output/Revision_Kit.pdf"):
    """
    Generates a 1-page revision kit based on academic content chunks.
    """
    # Retrieve the top N chunks from the collection
    results = collection.get(include=["documents"])
    all_chunks = results['documents']
    context = "\n\n".join(all_chunks[:total_chunks])

    # Build the prompt
    prompt = ChatPromptTemplate.from_template("""
You are a last-minute exam preparation assistant.

From the provided academic content, generate a 1-page revision kit that includes:
1. High-yield summary of key topics (concise points)
2. Important formulas, definitions, and concepts
3. 5 sample MCQs with answers (diverse and helpful for revision)

Structure the output clearly for fast revision.

--- START OF CONTENT ---
{context}
--- END OF CONTENT ---
""")

    formatted = prompt.format_messages(context=context)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    result = llm.invoke(formatted).content

    export_rescue_kit_to_pdf(result, filename)

def export_rescue_kit_to_pdf(text, filename="Data/Output/Revision_Kit.pdf"):
    """
    Exports the revision kit to a well-formatted PDF.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)

    for line in text.strip().split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)
    print(f"Revision Kit saved to: {filename}")
