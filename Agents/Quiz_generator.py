from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF

def run_quiz_generator(collection, total_chunks):
    results = collection.get(include=["documents"])
    all_chunks = results['documents']
    context = "\n\n".join(all_chunks[:total_chunks])

    prompt = ChatPromptTemplate.from_template("""
You are a quiz generation assistant.

Using ONLY the context provided, generate a diverse quiz with:
- 3 MCQs (1 mark each)
- 2 Short answer questions (3 marks each)
- 2 Long answer questions (5 marks each)
- 2 Fill in the blanks (1 mark each)
- 2 True/False (1 mark each)

Make the questions clear, educational, and well-structured. Format output with section titles like:
"Section: MCQs", "Section: Short Answer Questions", etc.

---
Context:
{context}
""")

    formatted_prompt = prompt.format_messages(context=context)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    response = llm.invoke(formatted_prompt)

    return response.content

def export_quiz_to_pdf(quiz_text, filename="Generated_Quiz.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in quiz_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)

    pdf.output(filename)
    print(f"Quiz saved as {filename}")
