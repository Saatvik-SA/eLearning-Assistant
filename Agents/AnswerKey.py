# --- Agents/AnswerKey.py ---

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF
import os

def run_answer_key_generator(quiz_text, filename="Generated_Answer_Key.pdf"):
    """
    Extracts correct answers from a generated quiz and exports them to a PDF.
    """
    prompt = ChatPromptTemplate.from_template("""
You are an academic assistant. The user has provided a quiz with different question types.
Your task is to extract only the correct **answers** from each question and format them under each section:

Use clear labels like:
"Section: MCQs - Answers"
"Section: Short Answer - Answers"
"Section: Long Answer - Answers"
"Section: Fill in the Blanks - Answers"
"Section: True/False - Answers"

Do NOT include the questions, just the answers.
If there are multiple correct options, list them clearly.

---
Quiz:
{quiz}
""")

    formatted_prompt = prompt.format_messages(quiz=quiz_text)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    answer_text = llm.invoke(formatted_prompt).content

    export_answer_key_to_pdf(answer_text, filename)

def export_answer_key_to_pdf(answer_text, filename="Generated_Answer_Key.pdf"):
    """
    Saves the answer key text to a PDF file.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in answer_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)

    pdf.output(filename)
    print(f"Answer key saved as {filename}")
