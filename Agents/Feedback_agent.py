from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF

def run_feedback_agent(graded_text, filename="Data/Output/Student_Feedback_Report.pdf"):
    prompt = ChatPromptTemplate.from_template("""
You are a helpful feedback assistant for students.

Given a graded quiz report, do the following:
1. Point out specific mistakes made in each question.
2. Suggest how to correct them or improve.
3. Summarize which key topics the student should revisit or focus on.
4. Be constructive and motivational in tone.

--- GRADED REPORT ---
{graded_text}
""")

    formatted = prompt.format_messages(graded_text=graded_text)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    feedback = llm.invoke(formatted).content

    export_feedback_to_pdf(feedback, filename)

def export_feedback_to_pdf(feedback_text, filename="Data/Output/Student_Feedback_Report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)

    for line in feedback_text.strip().split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)
    print(f"Feedback report exported: {filename}")
