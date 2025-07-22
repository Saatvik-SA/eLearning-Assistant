# nodes/query_expander_node.py

from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
import logging
from typing import Any, Dict
from Nodes.agent_state import AgentState, update_agent_state

AGENTIC_INTENTS = ["generate_plan", "generate_quiz", "generate_answer_key", "generate_revision_kit", "generate_quiz_grade", "generate_feedback", "track_progress", "send_notification", "rag_chat"]

AGENTIC_QUERY_EXPANDER_PROMPT = """
You are a smart, agentic AI for an eLearning Assistant. Your job is to deeply understand the user's request, even if it contains typos, creative phrasing, or ambiguous language. You must:
- Classify the user's intent as one of:
    - generate_plan: Create a study plan or schedule
    - generate_quiz: Generate a quiz or assessment
    - generate_answer_key: Generate answer key for existing quiz
    - generate_revision_kit: Generate a last-minute revision kit or rescue summary
    - generate_quiz_grade: Grade student quiz answers (single or batch)
    - generate_feedback: Generate feedback for a graded quiz or report
    - track_progress: Generate a progress report and chart from graded papers
    - send_notification: Send a report or reminder email to student/parent
    - rag_chat: Answer an academic question using uploaded/embedded context
    - unknown: If you truly cannot decide
- Extract any constraints (number of weeks, difficulty, number/type of questions, etc.)
- Explain your reasoning for the intent classification and constraint extraction.

Respond ONLY in the following JSON format:
{
  "intent": "generate_plan" | "generate_quiz" | "generate_answer_key" | "generate_revision_kit" | "generate_quiz_grade" | "generate_feedback" | "track_progress" | "send_notification" | "rag_chat" | "unknown",
  "reasoning": "...",
  "constraints": { ... }
}

---
Examples:
User query: "ask a question about history"
Output: {"intent": "rag_chat", "reasoning": "User wants to ask an academic question using RAG.", "constraints": {}}

User query: "explain Napoleon's reforms"
Output: {"intent": "rag_chat", "reasoning": "User wants an explanation of Napoleon's reforms using academic context.", "constraints": {}}

User query: "what is nationalism?"
Output: {"intent": "rag_chat", "reasoning": "User wants a definition of nationalism from the context.", "constraints": {}}

User query: "show my progress"
Output: {"intent": "track_progress", "reasoning": "User wants to see their progress over time.", "constraints": {}}

User query: "generate progress report"
Output: {"intent": "track_progress", "reasoning": "User wants a progress report.", "constraints": {}}

User query: "plot my scores"
Output: {"intent": "track_progress", "reasoning": "User wants a chart of their scores.", "constraints": {}}

User query: "how am i doing in my quizzes?"
Output: {"intent": "track_progress", "reasoning": "User wants an analysis of their quiz performance.", "constraints": {}}

User query: "i need a quiz, 5 mcqs, hard"
Output: {"intent": "generate_quiz", "reasoning": "User requested a quiz with 5 MCQs and hard difficulty.", "constraints": {"num_mcq": 5, "difficulty": "hard"}}

User query: "help me organize my revision"
Output: {"intent": "generate_plan", "reasoning": "User wants to organize revision, which means a study plan.", "constraints": {}}

User query: "test for chapter 2, easy"
Output: {"intent": "generate_quiz", "reasoning": "User wants a test (quiz) for chapter 2, easy difficulty.", "constraints": {"difficulty": "easy"}}

User query: "make answer key for quiz 1"
Output: {"intent": "generate_answer_key", "reasoning": "User wants an answer key for quiz 1.", "constraints": {"quiz_name": "quiz 1"}}

User query: "i need a last minute revision kit for my exam"
Output: {"intent": "generate_revision_kit", "reasoning": "User wants a revision kit for last-minute exam prep.", "constraints": {}}

User query: "grade my quiz answers"
Output: {"intent": "generate_quiz_grade", "reasoning": "User wants to grade quiz answers.", "constraints": {"grading_type": "single"}}

User query: "grade all student answers"
Output: {"intent": "generate_quiz_grade", "reasoning": "User wants to grade multiple student answers in batch.", "constraints": {"grading_type": "batch"}}

User query: "give me feedback on my graded quiz"
Output: {"intent": "generate_feedback", "reasoning": "User wants feedback on a graded quiz.", "constraints": {}}

User query: "can you review my quiz report and tell me what to improve?"
Output: {"intent": "generate_feedback", "reasoning": "User wants feedback and improvement suggestions for a graded report.", "constraints": {}}

User query: "give me a feedback for my graded papers"
Output: {"intent": "generate_feedback", "reasoning": "User wants feedback for already graded papers.", "constraints": {}}

User query: "review my graded answers"
Output: {"intent": "generate_feedback", "reasoning": "User wants a review of their graded answers.", "constraints": {}}

User query: "analyze my graded quiz"
Output: {"intent": "generate_feedback", "reasoning": "User wants analysis of a graded quiz.", "constraints": {}}

User query: "feedback for my marked paper"
Output: {"intent": "generate_feedback", "reasoning": "User wants feedback for a marked paper.", "constraints": {}}

User query: "asdfghjkl"
Output: {"intent": "unknown", "reasoning": "Input is gibberish.", "constraints": {}}

---
User query: "{{user_query}}"
Output:
"""

def agentic_query_expander_node() -> RunnableLambda:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    def expand_query(state: AgentState) -> AgentState:
        # If intent is already set (by CLI), do not re-classify
        if state.get("intent"):
            logging.info(f"[Query Expander] Intent already set in state: {state['intent']}. Skipping LLM classification.")
            return state
        user_query = state.get("most_recent_question") or state.get("query") or ""
        prompt = AGENTIC_QUERY_EXPANDER_PROMPT.replace("{{user_query}}", user_query)
        logging.info(f"[Query Expander] user_query: '{user_query}'")
        logging.info(f"[Query Expander] Prompt sent to LLM:\n{prompt}")
        try:
            response = llm.invoke(prompt)
            logging.info(f"[Query Expander] LLM raw response: {getattr(response, 'content', '')}")
            raw = getattr(response, "content", "").strip()
            # Try to parse JSON from LLM output
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                json_block = re.search(r'\{[\s\S]+\}', raw)
                if not json_block:
                    raise ValueError("No valid JSON found in response.")
                parsed = json.loads(json_block.group(0))
            intent = parsed.get("intent", "unknown")
            reasoning = parsed.get("reasoning", "")
            constraints = parsed.get("constraints", {}) or {}
            logging.info(f"[Query Expander] LLM intent: {intent}, reasoning: {reasoning}, constraints: {constraints}")
            if intent not in AGENTIC_INTENTS:
                logging.warning(f"[Query Expander] LLM could not determine intent. Asking user for clarification.")
                state.update({
                    "intent": "unknown",
                    "error": "Sorry, I couldn't understand your request. Please clarify: do you want to generate a study plan, quiz, answer key, revision kit, or grade quiz answers?",
                    "clarification_required": True,
                    "reasoning": reasoning
                })
                logging.info(f"[Query Expander] Returning state: {state}")
                return state
            state.update({
                "intent": intent,
                "reasoning": reasoning,
                "constraints": constraints,
                "revised_message": user_query
            })
            logging.info(f"[Query Expander] Returning state: {state}")
            return state
        except Exception as e:
            logging.error(f"[Query Expander] Error: {e}")
            return update_agent_state(
                state,
                intent="unknown",
                error="Sorry, I couldn't understand your request. Please clarify if you want a study plan, quiz, answer key, revision kit, or quiz grading.",
                clarification_required=True
            )
    return RunnableLambda(expand_query)
