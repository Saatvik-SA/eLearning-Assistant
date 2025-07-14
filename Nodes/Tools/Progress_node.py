from langchain_core.tools import tool
from Agents.Progress_tracker import track_progress
import os

@tool
def progress_tracker_node() -> dict:
    """
    Analyzes all graded student reports in Data/Output, extracts scores, and generates:
    - Progress_Report.csv
    - Progress_Chart_Line.png (line graph of performance)

    Returns:
    {
        "status": "completed",
        "csv_path": "Data/Output/Progress_Report.csv",
        "chart_path": "Data/Output/Progress_Chart_Line.png",
        "output_type": "file",
        "files_generated": [csv_path, chart_path]
    }
    """
    print("[Progress Tracker Node] Running progress tracker on graded reports...")

    track_progress(folder="Data/Output")

    csv_path = "Data/Output/Progress_Report.csv"
    chart_path = "Data/Output/Progress_Chart_Line.png"

    if not os.path.exists(csv_path) or not os.path.exists(chart_path):
        raise FileNotFoundError("Progress report or chart was not generated correctly.")

    return {
        "status": "completed",
        "csv_path": csv_path,
        "chart_path": chart_path,
        "output_type": "file",
        "files_generated": [csv_path, chart_path]
    }
