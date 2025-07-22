# Tools/quiz_generator_node.py

from Agents.Quiz_generator import run_quiz_generator_agent
from Nodes.agent_state import AgentState
import logging

def quiz_generator_node() -> callable:
    """
    Node for generating a quiz using syllabus content. Accepts and returns AgentState.
    """
    def node_fn(state: AgentState) -> AgentState:
        try:
            logging.info("[Quiz Generator Node] Running quiz generator agent...")
            return run_quiz_generator_agent(state)
        except Exception as e:
            logging.error(f"[Quiz Generator Node] Error: {e}")
            state["status"] = "error"
            state["error"] = str(e)
            return state
    return node_fn
