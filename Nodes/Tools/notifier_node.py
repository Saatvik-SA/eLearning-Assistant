# Tools/notifier_node.py

from langchain_core.tools import tool
from Agents.Notifier_agent import run_parent_notifier

def notifier_node(state: dict) -> dict:
    """
    Sends a report to the parent and/or reminders to the student.
    Attaches files based on user query: progress, study plan, or both.
    Mutates and returns state with status.
    """
    from Agents.Notifier_agent import run_parent_notifier
    import os
    # Determine what to attach based on user query/constraints
    user_query = state.get("input", "").lower()
    files_to_attach = []
    plan_path = "Data/Output/study_plan.xlsx"
    progress_csv = "Data/Output/Progress_Report.csv"
    progress_chart = "Data/Output/Progress_Chart_Line.png"
    if "progress" in user_query:
        if os.path.exists(progress_csv):
            files_to_attach.append(progress_csv)
        if os.path.exists(progress_chart):
            files_to_attach.append(progress_chart)
    if "plan" in user_query or "study plan" in user_query:
        if os.path.exists(plan_path):
            files_to_attach.append(plan_path)
    if "report" in user_query or "weekly" in user_query or not files_to_attach:
        # Attach all if generic or nothing matched
        if os.path.exists(plan_path):
            files_to_attach.append(plan_path)
        if os.path.exists(progress_csv):
            files_to_attach.append(progress_csv)
        if os.path.exists(progress_chart):
            files_to_attach.append(progress_chart)
    # Remove duplicates
    files_to_attach = list(dict.fromkeys(files_to_attach))
    try:
        run_parent_notifier(files_to_attach)
        state["status"] = "notified"
        state["output_type"] = "file"
        state["message"] = f"Notifier triggered: emailed files {files_to_attach}"
        state["tool_name"] = "notifier_node"
    except Exception as e:
        state["status"] = "error"
        state["error"] = str(e)
        state["tool_name"] = "notifier_node"
    return state

def notifier_node_wrapper():
    def node(state: dict) -> dict:
        return notifier_node(state)
    return node
