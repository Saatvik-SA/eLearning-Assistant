# --- File: Agents/Quiz_generator.py ---

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF
from datetime import datetime
import os

def run_quiz_generator(collection, total_chunks, num_mcq=3, num_short=2, num_long=2, num_fill=2, num_tf=2, difficulty=None):
    results = collection.get(include=["documents"])
    all_chunks = results['documents']
    context = "\n\n".join(all_chunks[:total_chunks])

    difficulty_prompt = f"Make the quiz {difficulty.lower()} level." if difficulty else ""

    prompt = ChatPromptTemplate.from_template(f"""
You are a quiz generation assistant.

Using ONLY the context provided, generate a quiz with:
- {num_mcq} MCQs (1 mark each)
- {num_short} Short answer questions (3 marks each)
- {num_long} Long answer questions (5 marks each)
- {num_fill} Fill in the blanks (1 mark each)
- {num_tf} True/False (1 mark each)

Make the questions clear, educational, and well-structured. Format output with section titles like:
"Section: MCQs", "Section: Short Answer Questions", etc.
{difficulty_prompt}
---
Context:
{{context}}
""")

    formatted_prompt = prompt.format_messages(context=context)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    response = llm.invoke(formatted_prompt)

    return response.content

def export_quiz_to_pdf(quiz_text, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Data/Output/Generated_Quiz_{timestamp}.pdf"

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in quiz_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)

    pdf.output(filename)
    print(f"Quiz saved as {filename}")

