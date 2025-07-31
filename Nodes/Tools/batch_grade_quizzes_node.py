# Tools/batch_grade_quizzes_node.py

from Agents.Quiz_grader import batch_grade_all_answers
from Utilities.Core import list_pdfs_in_directory, upload_answer_pdfs

def batch_grade_quizzes_node(inputs: dict) -> dict:
    """
    Grades all available student answer PDFs in Data/Answers.
    Saves reports in batch mode and returns list of output file paths.

    Returns:
    {
        "status": "batch_completed",
        "report_paths": [list of generated PDF reports],
        "multi_doc": true,
        "output_type": "file"
    }
    """
    answer_dir = "Data/Answers"
    available = list_pdfs_in_directory(answer_dir)
    if not available:
        print(f"No answer sheets found in {answer_dir}. Please upload the student answer sheet PDFs you want to grade.")
        uploaded = upload_answer_pdfs()
        if not uploaded:
            print("No answer sheets uploaded. Batch grading cancelled.")
            return {"status": "cancelled", "error": "No answer sheets uploaded.", "output_type": "file"}
    print("[Batch Grader Node] Grading all available student responses in Data/Answers...")
    report_paths = batch_grade_all_answers()

    return {
        "status": "batch_completed",
        "report_paths": report_paths,
        "multi_doc": True,
        "output_type": "file"
    }

def batch_grade_quizzes_node_wrapper() -> callable:
    def node(state: dict) -> dict:
        # Call the function with the state as input
        result = batch_grade_quizzes_node(state)
        # Merge result into state (preserve previous keys, update with result)
        state.update(result)
        state["tool_name"] = "batch_grade_quizzes_node"
        return state
    return node
