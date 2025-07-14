from langchain_core.tools import tool
from Agents.Feedback_agent import run_feedback_agent
from Utilities.PDF import extract_text_from_pdf_path
import os

@tool
def generate_feedback_node(inputs: dict) -> dict:
    """
    Generates personalized feedback from a graded quiz report and saves it as a PDF.

    Inputs:
    {
        "graded_file_path": "Data/Output/some_graded_file.pdf" or .txt,
        "student_name": Optional[str]
    }

    Output:
    {
        "status": "success",
        "file_path": <str>,
        "output_type": "file"
    }
    """
    graded_file_path = inputs.get("graded_file_path")
    student_name = inputs.get("student_name", "Student")

    if not graded_file_path or not os.path.exists(graded_file_path):
        raise FileNotFoundError(f"No valid graded file provided: {graded_file_path}")

    # Read text from the graded file (PDF or TXT)
    if graded_file_path.endswith(".pdf"):
        graded_text = extract_text_from_pdf_path(graded_file_path)
    elif graded_file_path.endswith(".txt"):
        with open(graded_file_path, "r", encoding="utf-8", errors="ignore") as f:
            graded_text = f.read()
    else:
        raise ValueError("Unsupported file type. Must be .pdf or .txt")

    # Construct feedback filename based on student or input
    student_name_clean = student_name.replace(" ", "_")
    feedback_filename = f"Data/Output/{student_name_clean}_Feedback_Report.pdf"

    # Run feedback agent → saves to PDF
    run_feedback_agent(graded_text, filename=feedback_filename)

    return {
        "status": "success",
        "file_path": feedback_filename,
        "output_type": "file"
    }
