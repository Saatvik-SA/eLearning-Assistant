# Tools/planner_node.py

from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from Agents.Planner_agent import run_study_planner, export_study_plan_to_excel

class PlannerInput(BaseModel):
    collection: object = Field(..., description="The ChromaDB collection of embedded syllabus chunks.")
    embedder: object = Field(..., description="The embedding model used to process academic content.")
    total_chunks: int = Field(..., description="Total number of content chunks in the collection.")
    weeks_before_exam: Optional[int] = Field(
        default=None,
        description="User-specified number of weeks remaining before the exam. Determines plan granularity."
    )

@tool(args_schema=PlannerInput)
def planner_node(inputs: PlannerInput) -> dict:
    """
    Generates a structured weekly study plan using syllabus content.
    Dynamically adapts the plan to the number of weeks before the exam as specified by the user.

    Returns metadata including path to the generated Excel file and summary of the plan.
    """
    print(f"[Planner Node] Generating study plan for {inputs.total_chunks} chunks over {inputs.weeks_before_exam or 'default'} weeks...")

    plan_df = run_study_planner(inputs.collection, inputs.total_chunks, weeks=inputs.weeks_before_exam)
    file_path = export_study_plan_to_excel(plan_df)

    summary = {
        "total_weeks": plan_df["Week"].nunique(),
        "total_chapters": plan_df["Chapter"].nunique(),
        "total_topics": plan_df["Key Topics/Concepts"].nunique()
    }

    return {
        "status": "success",
        "message": "Study plan generated successfully.",
        "output_file": file_path,
        "plan_summary": summary
    }
