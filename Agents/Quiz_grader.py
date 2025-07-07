# --- Agents/Quiz_grader.py ---

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF
import fitz
import os

from Utilities.PDF import extract_text_from_pdf_path
from Utilities.Embeddings import get_query_embedding
from Utilities.ChromaDB import query_chromadb_for_context
from Agents.Feedback_agent import run_feedback_agent


def run_grader(student_pdf_path: str):
    """
    Grades the student's answer sheet by retrieving relevant academic context from ChromaDB.
    No fixed quiz required.
    """
    student_answer_text = extract_text_from_pdf_path(student_pdf_path)

    # Get relevant context from ChromaDB
    student_embedding = get_query_embedding(student_answer_text)
    academic_context = query_chromadb_for_context(student_embedding)

    # Prompt to evaluate answer based on context
    prompt = ChatPromptTemplate.from_template("""
You are an academic evaluator assistant.

Evaluate the student's answers based on the academic content provided below.
Give marks if the answers demonstrate correct understanding, reasoning, and relevant facts.

Return:
1. A question-by-question breakdown (infer questions from student answers)
2. Marks per question
3. Total Score
4. Final feedback summary

--- ACADEMIC CONTEXT (SOURCE MATERIAL) ---
{context}

--- STUDENT ANSWERS ---
{student_answers}
""")

    formatted = prompt.format_messages(
        context=academic_context,
        student_answers=student_answer_text
    )

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    graded_output = llm.invoke(formatted)
    return graded_output.content


def export_graded_report_to_pdf(graded_text: str, filename="Student_Graded_Report.pdf"):
    """
    Saves graded report to PDF.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in graded_text.strip().split("\n"):
        pdf.multi_cell(0, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'))

    pdf.output(filename)
    print(f"Graded report exported: {filename}")


def batch_grade_all_answers(answers_folder="Data/Answers"):
    """
    Grades all answer PDFs in a folder using content from ChromaDB.
    """
    for file in os.listdir(answers_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(answers_folder, file)
            graded = run_grader(file_path)

            output_path = os.path.join("Data/Output", file.replace(".pdf", "_Graded.pdf"))
            export_graded_report_to_pdf(graded, filename=output_path)
            print(f"Graded: {file} → {output_path}")

            choice = input(f"Generate feedback for {file}? (yes/no): ").strip().lower()
            if choice in {"yes", "y"}:
                feedback_path = os.path.join("Data/Output", file.replace(".pdf", "_Feedback.txt"))
                run_feedback_agent(graded, filename=feedback_path)
                print(f"Feedback saved to: {feedback_path}")
