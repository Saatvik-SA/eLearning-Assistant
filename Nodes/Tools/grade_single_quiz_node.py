# Tools/grade_single_quiz_node.py

from Agents.Quiz_grader import run_grader, export_graded_report_to_pdf
from Agents.Quiz_generator import run_quiz_generator_agent
from Utilities.Core import select_pdf_file, prepare_academic_context

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
        # Instead of raising an error, prompt the user to upload the answer sheet
        return {
            "status": "awaiting_upload",
            "clarification_required": True,
            "error": "Please upload the student answer sheet PDF you want to grade.",
            "response": "Please upload the student answer sheet PDF you want to grade."
        }

    print(f"[Single Grader] Grading: {answer_pdf} | Subject: {subject}")

    # Grade the student's response (no need to generate a new quiz)
    graded_result = run_grader(answer_pdf)
    
    # Generate a proper filename for the graded report
    import os
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(answer_pdf))[0]
    report_filename = f"Data/Output/{base_name}_Graded_{timestamp}.pdf"
    
    report_path = export_graded_report_to_pdf(graded_result, report_filename)

    return {
        "status": "graded",
        "report_path": report_path,
        "graded_data": graded_result,
        "output_type": "file"
    }

def grade_single_quiz_node_wrapper() -> callable:
    def node(state: dict) -> dict:
        # Call the function with the state as input
        result = grade_single_quiz_node(state)
        # Merge result into state (preserve previous keys, update with result)
        state.update(result)
        return state
    return node
