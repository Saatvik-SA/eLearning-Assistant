# Tools/notifier_node.py

from langchain_core.tools import tool
from Agents.Notifier_agent import run_parent_notifier

@tool
def notifier_node(trigger: str = "weekly"):
    """
    Sends a report to the parent and/or reminders to the student.
    Trigger values can be:
    - 'weekly' → sends weekly progress and plan to parent + reminder to student
    - 'initial' → sends full study plan to parent (first time only)
    - 'manual' → sends a report manually on request

    It pulls data from:
    - Data/Output/Progress_Report.csv
    - Data/Output/Progress_Chart_Line.png
    - Data/Planner/study_plan.xlsx

    Email is sent based on .env settings.

    Args:
        trigger (str): Type of notification trigger. One of ["weekly", "initial", "manual"]
    """
    run_parent_notifier(trigger_type=trigger)
    return f"Notifier triggered with: {trigger}"
