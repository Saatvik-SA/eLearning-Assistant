# --- Agents/Planner_agent.py ---

import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from Nodes.agent_state import AgentState, update_agent_state
from typing import Optional
import os

def run_study_planner_agent(state: AgentState) -> AgentState:
    """
    Generates a weekly study plan using the academic context in state.
    Expects: collection, total_chunks, and optionally weeks_left (from constraints or user input).
    Updates state with the plan text and output file path.
    """
    try:
        collection = state.get("collection")
        total_chunks = state.get("total_chunks")
        constraints = state.get("constraints", {})
        weeks_left = constraints.get("weeks_left") or constraints.get("weeks_before_exam")
        if weeks_left is None:
            try:
                weeks_left = int(input("How many weeks until your exam? ").strip())
            except Exception:
                print("Invalid input. Defaulting to 6 weeks.")
                weeks_left = 6
        # Extract top chunks from collection
        results = collection.get(include=["documents"])
        all_chunks = results["documents"]
        context = "\n\n".join(all_chunks[:total_chunks])
        # Prompt for detailed structured output
        prompt = ChatPromptTemplate.from_template("""
You are an educational planner agent.

Use ONLY the academic content below to create a detailed weekly study plan for {weeks_left} weeks.

For each week, extract meaningful topics and break them into structured columns:
- Week (as numbers: 1, 2, ...)
- Section (e.g., I, II, III — optional if unknown)
- Chapter (e.g., I, II, III — optional if unknown)
- Key Topics/Concepts (core concepts for the week)
- Description (1-line helpful summary)

Return the result as a markdown table with headers:
| Week | Section | Chapter | Key Topics/Concepts | Description |

---
Content:
{context}
""")
        formatted_prompt = prompt.format_messages(
            context=context,
            weeks_left=weeks_left
        )
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        response = llm.invoke(formatted_prompt)
        plan_text = response.content
        # Export to Excel
        file_path = export_study_plan_to_excel(plan_text)
        # Update state
        return update_agent_state(
            state,
            plan_text=plan_text,
            files=[file_path],
            file_path=file_path,
            output_type="file",
            response="Study plan generated successfully.",
            status="done",
            tool_name="planner_node"
        )
    except Exception as e:
        return update_agent_state(state, status="error", error=str(e), tool_name="planner_node")

def export_study_plan_to_excel(response_text: str, filename="Data/Output/study_plan.xlsx") -> str:
    lines = response_text.strip().splitlines()
    table_lines = [line for line in lines if "|" in line and not line.strip().startswith("---")]
    # Split rows on pipes
    rows = [line.strip().split("|")[1:-1] for line in table_lines if line.count("|") >= 5]
    rows = [list(map(str.strip, row)) for row in rows]
    if not rows or len(rows[0]) < 5:
        print("Couldn't extract structured table. Please check LLM output.")
        return filename
    import pandas as pd
    df = pd.DataFrame(rows, columns=["Week", "Section", "Chapter", "Key Topics/Concepts", "Description"])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_excel(filename, index=False)
    print(f"Study plan saved to: {filename}")
    return filename
