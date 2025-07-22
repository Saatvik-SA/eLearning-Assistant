import os
from Agents.Progress_tracker import track_progress

def progress_tracker_node(state: dict) -> dict:
    """
    Analyzes all graded student reports in Data/Output, extracts scores, and generates:
    - Progress_Report.csv
    - Progress_Chart_Line.png (line graph of performance)

    Mutates and returns state with file paths and status.
    """

    print("[Progress Tracker Node] Running progress tracker on graded reports...")
    track_progress(folder="Data/Output")

    csv_path = "Data/Output/Progress_Report.csv"
    chart_path = "Data/Output/Progress_Chart_Line.png"

    if not os.path.exists(csv_path) or not os.path.exists(chart_path):
        state["status"] = "error"
        state["error"] = "Progress report or chart was not generated correctly."
        return state

    state["status"] = "completed"
    state["csv_path"] = csv_path
    state["chart_path"] = chart_path
    state["output_type"] = "file"
    state["files_generated"] = [csv_path, chart_path]
    return state

def progress_node_wrapper():
    def node(state: dict) -> dict:
        return progress_tracker_node(state)
    return node
