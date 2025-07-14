# --- Agents/AnswerKey.py ---

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF
import urllib.request
import os

from Utilities.PDF import extract_text_from_pdf_path
from Utilities.Core import prepare_academic_context

def run_answer_key_generator():
    """
    Extracts correct answers from a quiz file in Data/Upload and exports them to a PDF in Data/Output,
    using textbook context embedded via `prepare_academic_context()`.
    """

    # Step 1: Locate a quiz file with "quiz" in its name
    upload_dir = "Data/Upload"
    quiz_file = None
    for file in os.listdir(upload_dir):
        if "quiz" in file.lower() and file.lower().endswith((".pdf", ".txt")):
            quiz_file = os.path.join(upload_dir, file)
            break

    if not quiz_file:
        raise FileNotFoundError("No quiz file with 'quiz' in name (.pdf or .txt) found in Data/Upload.")

    # Step 2: Extract quiz text
    if quiz_file.endswith(".pdf"):
        quiz_text = extract_text_from_pdf_path(quiz_file)
    else:
        with open(quiz_file, "r", encoding="utf-8") as f:
            quiz_text = f.read()

    # Step 3: Retrieve textbook context using Core utilities
    collection, embedder, total_chunks = prepare_academic_context()
    results = collection.query(query_texts=[quiz_text], n_results=8)
    context_text = "\n".join(results['documents'][0])

    # Step 4: Prompt to generate answer key
    prompt = ChatPromptTemplate.from_template("""
You are an academic assistant. The user has provided a quiz with different question types and related textbook content.
Your task is to extract only the correct **answers** from each question, leveraging the textbook context, and format them under each section:

Use clear labels like:
"Section: MCQs - Answers"
"Section: Short Answer - Answers"
"Section: Long Answer - Answers"
"Section: Fill in the Blanks - Answers"
"Section: True/False - Answers"

Do NOT include the questions, just the answers.
Use the provided context to extract the most likely correct responses.

---
Context:
{context}

---
Quiz:
{quiz}
""")

    formatted_prompt = prompt.format_messages(context=context_text, quiz=quiz_text)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    answer_text = llm.invoke(formatted_prompt).content

    # Step 5: Export answer key
    base_name = os.path.splitext(os.path.basename(quiz_file))[0]
    output_file = os.path.join("Data/Output", f"{base_name}_answer_key.pdf")
    export_answer_key_to_pdf(answer_text, output_file)


def export_answer_key_to_pdf(answer_text, filename="Generated_Answer_Key.pdf"):
    """
    Saves the answer key text to a PDF file (basic ASCII, Arial only).
    Will skip unsupported characters silently.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12) 

    for line in answer_text.split('\n'):
        try:
            pdf.multi_cell(0, 10, txt=line.encode('latin-1', 'ignore').decode('latin-1'))
        except Exception as e:
            print(f"Warning: Skipped line due to encoding issue: {line}")

    pdf.output(filename)
    print(f"Answer key saved as {filename}")

