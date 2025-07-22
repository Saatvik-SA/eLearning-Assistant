# nodes/intent_router_node.py

from langchain_core.runnables import RunnableLambda
from Nodes.agent_state import AgentState, update_agent_state
import logging

def intent_router_node() -> RunnableLambda:
    """
    Routes the agentic intent to the correct node. Supports 'generate_plan' and 'generate_quiz' intents. Handles unknown intent gracefully.
    """
    def classify_and_route(state: AgentState) -> AgentState:
        logging.info(f"[Intent Router] Full state: {state}")
        # Try to extract intent from top-level, then from any nested dicts
        intent = state.get("intent", "").strip()
        if not intent:
            # Check for nested dicts (e.g., 'expanded' or others)
            for v in state.values():
                if isinstance(v, dict) and "intent" in v:
                    intent = v["intent"].strip()
                    break
        logging.info(f"[Intent Router] Extracted intent: {intent}")
        if intent == "generate_plan":
            return update_agent_state(state, tool_name="planner_node")
        elif intent == "generate_quiz":
            return update_agent_state(state, tool_name="quiz_generator_node")
        elif intent == "generate_answer_key":
            return update_agent_state(state, tool_name="answer_key_node")
        elif intent == "generate_revision_kit":
            return update_agent_state(state, tool_name="revision_kit_node")
        elif intent == "generate_quiz_grade":
            # Check number of answer files in Data/Answers
            import os
            answers_dir = "Data/Answers"
            if os.path.exists(answers_dir):
                answer_files = [f for f in os.listdir(answers_dir) if f.lower().endswith('.pdf')]
                num_files = len(answer_files)
            else:
                num_files = 0
            if num_files > 1:
                return update_agent_state(state, tool_name="batch_grade_quizzes_node")
            else:
                return update_agent_state(state, tool_name="grade_single_quiz_node")
        elif intent == "generate_feedback":
            return update_agent_state(state, tool_name="feedback_node")
        elif intent == "track_progress":
            return update_agent_state(state, tool_name="progress_node")
        elif intent == "send_notification":
            return update_agent_state(state, tool_name="notifier_node")
        elif intent == "rag_chat":
            return update_agent_state(state, tool_name="rag_chat_node")
        else:
            logging.error(f"[Intent Router] Unsupported or missing intent: {intent}")
            return update_agent_state(state, status="error", error="Sorry, I could not understand your request. Please clarify if you want a study plan, quiz, answer key, revision kit, or quiz grading.")
    return RunnableLambda(classify_and_route)
