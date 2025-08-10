# nodes/tools/answer_key_node.py

from Agents.AnswerKey import run_answer_key_generator
from Nodes.agent_state import AgentState
import logging

def answer_key_node() -> callable:
    """
    Node for generating answer key using the AnswerKey agent.
    Accepts and returns AgentState.
    """
    def node_fn(state: AgentState) -> AgentState:
        try:
            logging.info("[Answer Key Node] Running answer key generator agent...")
            # Run the answer key generator agent with state
            return run_answer_key_generator(state)
        except Exception as e:
            logging.error(f"[Answer Key Node] Error: {e}")
            return update_agent_state(
                state, 
                status="error", 
                error=str(e),
                tool_name="answer_key_node"
            )
    return node_fn
