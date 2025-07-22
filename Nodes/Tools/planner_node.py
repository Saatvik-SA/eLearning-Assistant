# Tools/planner_node.py

from Agents.Planner_agent import run_study_planner_agent
from Nodes.agent_state import AgentState
import logging

def planner_node() -> callable:
    """
    Node for generating a structured weekly study plan using syllabus content.
    Accepts and returns AgentState.
    """
    def node_fn(state: AgentState) -> AgentState:
        try:
            logging.info("[Planner Node] Running study planner agent...")
            return run_study_planner_agent(state)
        except Exception as e:
            logging.error(f"[Planner Node] Error: {e}")
            state["status"] = "error"
            state["error"] = str(e)
            return state
    return node_fn
