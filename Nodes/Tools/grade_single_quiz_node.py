# Tools/grade_single_quiz_node.py

from Agents.Quiz_grader import run_grader, export_graded_report_to_pdf
from Agents.Quiz_generator import run_quiz_generator_agent
from Utilities.Core import select_pdf_file, prepare_academic_context, list_pdfs_in_directory, prompt_user_to_select_file, upload_answer_pdfs
from Utilities.PDF import export_graded_report_to_pdf

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
        # List available answer PDFs
        answer_dir = "Data/Answers"
        available = list_pdfs_in_directory(answer_dir)
        if available:
            print(f"Found {len(available)} answer sheet(s) in {answer_dir}:")
            for f in available:
                print(f"→ {f}")
            selected = prompt_user_to_select_file(available, "Select an answer sheet for grading (number): ")
            if selected:
                answer_pdf = os.path.join(answer_dir, selected)
            else:
                print("No answer sheet selected. Grading cancelled.")
                return {"status": "cancelled", "error": "No answer sheet selected."}
        else:
            print(f"No answer sheets found in {answer_dir}. Please upload the student answer sheet PDF you want to grade.")
            uploaded = upload_answer_pdfs()
            if uploaded:
                answer_pdf = uploaded[-1]
                print(f"Uploaded: {answer_pdf}")
            else:
                print("No answer sheet uploaded. Grading cancelled.")
                return {"status": "cancelled", "error": "No answer sheet uploaded."}
    print(f"[Single Grader] Grading: {answer_pdf} | Subject: {subject}")
    graded_result = run_grader(answer_pdf)
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
        state["tool_name"] = "grade_single_quiz_node"
        return state
    return node
