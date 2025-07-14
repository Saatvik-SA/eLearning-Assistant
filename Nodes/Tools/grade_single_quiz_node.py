# Tools/grade_single_quiz_node.py

from langchain_core.tools import tool
from Agents.Quiz_grader import run_grader, export_graded_report_to_pdf
from Agents.Quiz_generator import run_quiz_generator
from Utilities.Core import select_pdf_file, prepare_academic_context

@tool
def grade_single_quiz_node(inputs: dict) -> dict:
    """
    Grades a single student answer sheet based on a freshly generated quiz.
    Returns the grading summary and path to PDF report.
    
    Expects:
    {
        "file_reference": "<path_to_answer_pdf>",
        "subject": "<quiz subject>"
    }
    """
    answer_pdf = inputs.get("file_reference")
    subject = inputs.get("subject", "unknown")

    if not answer_pdf:
        raise ValueError("Missing file_reference: no student answer sheet provided.")

    print(f"[Single Grader] Grading: {answer_pdf} | Subject: {subject}")

    # Prepare context
    collection, embedder, total_chunks = prepare_academic_context()

    # Generate quiz based on same context
    quiz = run_quiz_generator(collection, total_chunks)

    # Grade the student's response
    graded_result = run_grader(answer_pdf)
    report_path = export_graded_report_to_pdf(graded_result)

    return {
        "status": "graded",
        "report_path": report_path,
        "graded_data": graded_result,
        "output_type": "file"
    }
