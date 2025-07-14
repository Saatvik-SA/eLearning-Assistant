# Tools/batch_grade_quizzes_node.py

from langchain_core.tools import tool
from Agents.Quiz_grader import batch_grade_all_answers

@tool
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
    print("[Batch Grader Node] Grading all available student responses in Data/Answers...")

    report_paths = batch_grade_all_answers()

    return {
        "status": "batch_completed",
        "report_paths": report_paths,
        "multi_doc": True,
        "output_type": "file"
    }
