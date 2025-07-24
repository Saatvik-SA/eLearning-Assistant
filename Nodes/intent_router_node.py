# nodes/intent_router_node.py

from langchain_core.runnables import RunnableLambda
from Nodes.agent_state import AgentState, update_agent_state
import logging

def intent_router_node() -> RunnableLambda:
    """
    Routes the agentic intent to the correct node using a mapping. Handles unknown intent gracefully.
    """
    INTENT_TO_TOOL = {
        "generate_plan": "planner_node",
        "generate_quiz": "quiz_generator_node",
        "generate_answer_key": "answer_key_node",
        "generate_revision_kit": "revision_kit_node",
        "generate_feedback": "feedback_node",
        "track_progress": "progress_node",
        "send_notification": "notifier_node",
        "rag_chat": "rag_chat_node",
    }

    def grading_tool_router(state):
        import os
        answers_dir = "Data/Answers"
        if os.path.exists(answers_dir):
            answer_files = [f for f in os.listdir(answers_dir) if f.lower().endswith('.pdf')]
            num_files = len(answer_files)
        else:
            num_files = 0
        if num_files > 1:
            return "batch_grade_quizzes_node"
        else:
            return "grade_single_quiz_node"

    def classify_and_route(state: AgentState) -> AgentState:
        logging.info(f"[Intent Router] Full state: {state}")
        intent = state.get("intent", "").strip()
        if not intent:
            for v in state.values():
                if isinstance(v, dict) and "intent" in v:
                    intent = v["intent"].strip()
                    break
        logging.info(f"[Intent Router] Extracted intent: {intent}")
        if intent == "generate_quiz_grade":
            tool_name = grading_tool_router(state)
        else:
            tool_name = INTENT_TO_TOOL.get(intent)
        if tool_name:
            return update_agent_state(state, tool_name=tool_name)
        else:
            logging.error(f"[Intent Router] Unsupported or missing intent: {intent}")
            return update_agent_state(state, status="error", error="Sorry, I could not understand your request. Please clarify if you want a study plan, quiz, answer key, revision kit, or quiz grading.")
    return RunnableLambda(classify_and_route)
