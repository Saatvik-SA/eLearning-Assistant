# --- Agents/Quiz_generator.py ---

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from Nodes.agent_state import AgentState, update_agent_state
from Utilities.PDF import extract_texts_from_folder
from Utilities.Core import prepare_academic_context
from datetime import datetime
import os
import logging

def run_quiz_generator_agent(state: AgentState) -> AgentState:
    """
    Generates a quiz using the academic context in state.
    Reads all quiz parameters from state/constraints. Exports quiz to PDF. Updates state with output_type, file_path, and preview.
    """
    try:
        collection = state.get("collection")
        total_chunks = state.get("total_chunks")
        constraints = state.get("constraints", {})
        num_mcq = constraints.get("num_mcq", 3)
        num_short = constraints.get("num_short", 2)
        num_long = constraints.get("num_long", 2)
        num_fill = constraints.get("num_fill", 2)
        num_tf = constraints.get("num_tf", 2)
        difficulty = constraints.get("difficulty")
        # Extract top chunks from collection
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

Make the questions clear, educational, and well-structured.
Format output with section titles like:
"Section: MCQs", "Section: Short Answer Questions", etc.
{difficulty_prompt}

---
Context:
{{context}}
""")
        formatted_prompt = prompt.format_messages(context=context)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        response = llm.invoke(formatted_prompt)
        quiz_text = response.content
        # Export to PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"Data/Output/Generated_Quiz_{timestamp}.pdf"
        export_quiz_to_pdf(quiz_text, file_path)
        logging.info(f"Quiz generated and saved to {file_path}")
        return update_agent_state(
            state,
            quiz_text=quiz_text,
            files=[file_path],
            file_path=file_path,
            output_type="file",
            quiz_preview=quiz_text[:1000],
            response="Quiz generated successfully.",
            status="done",
            tool_name="quiz_generator_node"
        )
    except Exception as e:
        logging.error(f"Quiz generation failed: {e}")
        return update_agent_state(state, status="error", error=str(e), tool_name="quiz_generator_node")

def export_quiz_to_pdf(quiz_text, filename):
    """
    Exports the generated quiz text into a PDF.
    """
    from fpdf import FPDF
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in quiz_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)
    pdf.output(filename)
    print(f"Quiz saved as {filename}")
