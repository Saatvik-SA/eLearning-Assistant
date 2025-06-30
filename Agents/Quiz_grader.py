from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF
import fitz

def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text.strip()

def run_grader(quiz_text: str, student_pdf_path: str):
    student_answer_text = extract_text_from_pdf(student_pdf_path)

    prompt = ChatPromptTemplate.from_template("""
You are an academic evaluator agent.

Given the quiz questions and a student's answer sheet, assign marks to each question. Follow these rules:
- For MCQs, True/False, and Fill-in-the-blanks, expect exact answers (1 mark each).
- For short/long answers, award marks if the intent is correct and key concepts/terms are present.
- Include the correct answer, the student's answer, marks given, and a brief explanation.

--- QUIZ QUESTIONS ---
{quiz}

--- STUDENT ANSWERS ---
{student_answers}

Now grade each question and return:
1. A question-by-question breakdown with:
   - Question
   - Correct Answer
   - Student Answer
   - Marks Awarded
   - Explanation
2. Total Score
""")

    formatted_prompt = prompt.format_messages(
        quiz=quiz_text,
        student_answers=student_answer_text
    )

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    graded_output = llm.invoke(formatted_prompt)
    return graded_output.content

def export_graded_report_to_pdf(graded_text: str, filename="Student_Graded_Report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in graded_text.strip().split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)
    print(f"Graded report exported: {filename}")
