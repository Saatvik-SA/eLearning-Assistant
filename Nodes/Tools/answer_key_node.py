# nodes/tools/answer_key_node.py

from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF
import os
import logging
from typing import Any, Dict
from Nodes.agent_state import AgentState, update_agent_state

from Utilities.PDF import extract_text_from_pdf_path
from Utilities.Core import prepare_academic_context

def answer_key_node() -> RunnableLambda:
    """
    Generates answer key for existing quiz files using textbook context.
    """
    def generate_answer_key(state: AgentState) -> AgentState:
        logging.info(f"[Answer Key Node] Starting answer key generation with state: {state}")
        
        try:
            # Get constraints from state
            constraints = state.get("constraints", {})
            quiz_name = constraints.get("quiz_name", "")
            
            # Step 1: Locate quiz file
            upload_dir = "Data/Upload"
            quiz_file = None
            
            # If specific quiz name provided, try to find it
            if quiz_name:
                for file in os.listdir(upload_dir):
                    if quiz_name.lower() in file.lower() and file.lower().endswith((".pdf", ".txt")):
                        quiz_file = os.path.join(upload_dir, file)
                        break
            
            # If no specific quiz or not found, look for any quiz file
            if not quiz_file:
                for file in os.listdir(upload_dir):
                    if "quiz" in file.lower() and file.lower().endswith((".pdf", ".txt")):
                        quiz_file = os.path.join(upload_dir, file)
                        break

            if not quiz_file:
                error_msg = f"No quiz file found in Data/Upload. Please upload a quiz file first."
                logging.error(f"[Answer Key Node] {error_msg}")
                return update_agent_state(
                    state,
                    status="error",
                    error=error_msg,
                    tool_name="answer_key_node"
                )

            logging.info(f"[Answer Key Node] Found quiz file: {quiz_file}")

            # Step 2: Extract quiz text
            if quiz_file.endswith(".pdf"):
                quiz_text = extract_text_from_pdf_path(quiz_file)
            else:
                with open(quiz_file, "r", encoding="utf-8") as f:
                    quiz_text = f.read()

            logging.info(f"[Answer Key Node] Extracted quiz text length: {len(quiz_text)}")

            # Step 3: Retrieve textbook context
            collection, embedder, total_chunks = prepare_academic_context()
            results = collection.query(query_texts=[quiz_text], n_results=8)
            context_text = "\n".join(results['documents'][0])

            logging.info(f"[Answer Key Node] Retrieved context length: {len(context_text)}")

            # Step 4: Generate answer key using LLM
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

            logging.info(f"[Answer Key Node] Generated answer key length: {len(answer_text)}")

            # Step 5: Export answer key
            base_name = os.path.splitext(os.path.basename(quiz_file))[0]
            output_file = os.path.join("Data/Output", f"{base_name}_answer_key.pdf")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Export to PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            for line in answer_text.split('\n'):
                try:
                    pdf.multi_cell(0, 10, txt=line.encode('latin-1', 'ignore').decode('latin-1'))
                except Exception as e:
                    logging.warning(f"[Answer Key Node] Skipped line due to encoding issue: {line}")

            pdf.output(output_file)
            
            logging.info(f"[Answer Key Node] Answer key saved as: {output_file}")

            # Update state with success
            return update_agent_state(
                state,
                status="success",
                result=f"Answer key generated successfully! Saved as: {output_file}",
                output_file=output_file,
                answer_key_text=answer_text,
                tool_name="answer_key_node"
            )

        except Exception as e:
            error_msg = f"Error generating answer key: {str(e)}"
            logging.error(f"[Answer Key Node] {error_msg}")
            return update_agent_state(
                state,
                status="error",
                error=error_msg,
                tool_name="answer_key_node"
            )

    return RunnableLambda(generate_answer_key)
