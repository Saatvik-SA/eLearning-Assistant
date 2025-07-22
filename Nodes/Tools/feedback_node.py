import os
from Agents.Feedback_agent import run_feedback_agent
from Utilities.PDF import extract_text_from_pdf_path

# Remove @tool and Pydantic schema
def feedback_node(state: dict) -> dict:
    """
    Generates personalized feedback from a graded quiz report and saves it as a PDF.
    Expects:
        state['graded_file_path']: path to graded PDF or TXT
        state['student_name']: optional
    Mutates and returns state with feedback file path and status.
    """
    graded_file_path = state.get("graded_file_path")
    student_name = state.get("student_name", "Student")

    if not graded_file_path or not os.path.exists(graded_file_path):
        state["status"] = "error"
        state["error"] = f"No valid graded file provided: {graded_file_path}"
        return state

    # Read text from the graded file (PDF or TXT)
    if graded_file_path.endswith(".pdf"):
        graded_text = extract_text_from_pdf_path(graded_file_path)
    elif graded_file_path.endswith(".txt"):
        with open(graded_file_path, "r", encoding="utf-8", errors="ignore") as f:
            graded_text = f.read()
    else:
        state["status"] = "error"
        state["error"] = "Unsupported file type. Must be .pdf or .txt"
        return state

    # Construct feedback filename based on student or input
    student_name_clean = student_name.replace(" ", "_")
    feedback_filename = f"Data/Output/{student_name_clean}_Feedback_Report.pdf"

    # Run feedback agent → saves to PDF
    run_feedback_agent(graded_text, filename=feedback_filename)

    state["status"] = "success"
    state["file_path"] = feedback_filename
    state["output_type"] = "file"
    return state

def feedback_node_wrapper():
    def node(state: dict) -> dict:
        return feedback_node(state)
    return node
