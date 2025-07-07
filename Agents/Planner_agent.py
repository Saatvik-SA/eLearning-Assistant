# --- Agents/Planner_agent.py ---

import os
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

def run_study_planner(collection, total_chunks, weeks_left):
    """
    Generates a weekly study plan based on syllabus content chunks.
    """
    results = collection.get(include=["documents"])
    all_chunks = results['documents']
    context = "\n\n".join(all_chunks[:total_chunks])

    prompt = ChatPromptTemplate.from_template("""
You are an educational planner agent.

Create a weekly study plan using ONLY the provided academic content.

Divide the material into {weeks_left} weeks.
Each week should list key topics or concepts with brief 1-line descriptions.
Format your output in a table-like structure.

--- CONTENT START ---
{context}
--- CONTENT END ---
""")

    formatted_prompt = prompt.format_messages(
        context=context,
        weeks_left=weeks_left
    )

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    response = llm.invoke(formatted_prompt)

    return response.content

def export_study_plan_to_excel(response_text: str, filename="Data/Output/study_plan.xlsx"):
    """
    Saves the study plan to an Excel sheet.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = []
    current_week = ""

    for line in response_text.strip().split("\n"):
        line = line.strip()
        if line.lower().startswith("week"):
            current_week = line
        elif line:
            data.append([current_week, line])

    df = pd.DataFrame(data, columns=["Week", "Topic / Plan"])
    df.to_excel(filename, index=False)
    print(f"Study plan exported to: {filename}")
