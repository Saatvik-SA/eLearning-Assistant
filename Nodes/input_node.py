# nodes/input_node.py
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage
import logging
from typing import Any, Dict
from Nodes.agent_state import AgentState, update_agent_state

def input_node() -> RunnableLambda:
    """
    Captures user input and uploaded file paths, initializes or updates AgentState.
    Adds textbook name/path if available for downstream context.
    """
    def format_input(state: Dict[str, Any]) -> AgentState:
        try:
            user_input = state.get("input", "").strip()
            uploaded_files = state.get("uploaded_files", [])
            textbook = state.get("textbook") or (uploaded_files[0] if uploaded_files else None)
            messages = state.get("messages", [])
            messages = list(messages) + [HumanMessage(content=user_input)]
            agent_state = update_agent_state(
                state,
                messages=messages,
                most_recent_question=user_input,
                uploaded_files=uploaded_files,
                textbook=textbook,
                tool_call_completed=False,
                image_chunk_map={},
            )
            logging.info(f"[Input Node] Received input: {user_input}")
            return agent_state
        except Exception as e:
            logging.error(f"[Input Node] Error: {e}")
            return update_agent_state(state, error=str(e))
    return RunnableLambda(format_input)