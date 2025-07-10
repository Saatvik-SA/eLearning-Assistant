# --- Agents/Planner_agent.py ---

import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


def run_study_planner(collection, total_chunks, weeks_left=None):
    # Ask user for number of weeks if not passed
    if weeks_left is None:
        try:
            weeks_left = int(input("How many weeks until your exam? ").strip())
        except:
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
    return response.content


def export_study_plan_to_excel(response_text: str, filename="Data/Output/study_plan.xlsx"):
    lines = response_text.strip().splitlines()
    table_lines = [line for line in lines if "|" in line and not line.strip().startswith("---")]

    # Split rows on pipes
    rows = [line.strip().split("|")[1:-1] for line in table_lines if line.count("|") >= 5]
    rows = [list(map(str.strip, row)) for row in rows]

    if not rows or len(rows[0]) < 5:
        print("Couldn't extract structured table. Please check LLM output.")
        return

    df = pd.DataFrame(rows, columns=["Week", "Section", "Chapter", "Key Topics/Concepts", "Description"])
    df.to_excel(filename, index=False)
    print(f"Study plan saved to: {filename}")
