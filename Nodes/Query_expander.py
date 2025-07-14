# nodes/query_expander_node.py

from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re

# === SYSTEM PROMPT ===
EXPANSION_SYSTEM_PROMPT = """
You are an intelligent agent designed to support advanced, structured problem-solving in the educational domain through reasoning over syllabus documents, instructional content, assessments, and learner data.

Your role is to interpret user requests related to learning goals and classroom materials, expand vague queries into structured formats, and route them to the appropriate educational tool or workflow for execution.

You are an expert assistant in E-Learning automation and curriculum-driven personalization. Your responsibilities include analyzing learning documents, generating assessments, grading submissions, planning study schedules, tracking learner progress, and preparing feedback or reports.

You must convert natural language input into precise, structured commands for downstream tools, using reasoning across document context, metadata, file references, learning intent, and constraints.

Your Output Must Follow:
{
  "intent": "one of: generate_plan | generate_quiz | grade_quiz | generate_key | provide_feedback | answer_question | track_progress | notify_user",
  "subject": "topic name or course area",
  "file_reference": "relevant uploaded document if any",
  "constraints": {
    "num_questions": optional integer,
    "difficulty": optional string,
    "timeframe": optional string or range,
    "output_format": "pdf | csv | text | chart | notification",
    "notify": true | false
  },
  "output_type": "chat | file | dashboard | email"
}

Guidelines:
- Resolve vague inputs using chat history (“this”, “it”, etc.)
- Return only structured JSON, no explanation
- If missing info, use "unknown" or null
- Default to pdf output for generation tasks

Example:
Input: "Make a quiz from this"
Output:
{
  "intent": "generate_quiz",
  "subject": "machine learning",
  "file_reference": "uploads/ml_notes.pdf",
  "constraints": { "num_questions": 10 },
  "output_type": "file"
}
"""

def query_expander_node() -> RunnableLambda:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    def expand_query(inputs: dict) -> dict:
        query = inputs.get("query", "")
        uploaded_files = inputs.get("uploaded_files", [])
        file_reference = uploaded_files[0] if uploaded_files else None

        full_prompt = EXPANSION_SYSTEM_PROMPT + f'\n\nInput: "{query}"\nOutput:\n'

        try:
            response = llm.invoke(full_prompt)
            print("\n FULL LLM RESPONSE OBJECT:\n", response)

            raw = getattr(response, "content", "").strip()

            # Try loading as JSON
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                # Try to extract JSON block manually
                json_block = re.search(r'\{[\s\S]+\}', raw)
                if not json_block:
                    raise ValueError("No valid JSON found in response.")
                parsed = json.loads(json_block.group(0))

            # Inject file reference if model didn't fill it
            if not parsed.get("file_reference") and file_reference:
                parsed["file_reference"] = file_reference

            return {
                **inputs,
                "expanded": parsed,
                "revised_query": query
            }

        except Exception as e:
            print("Query expansion failed:", str(e))
            return {
                **inputs,
                "expanded": {
                    "intent": "unknown",
                    "subject": None,
                    "file_reference": file_reference,
                    "constraints": {},
                    "output_type": "chat"
                },
                "revised_query": query
            }

    return RunnableLambda(expand_query)
