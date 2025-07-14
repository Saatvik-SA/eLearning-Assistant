# agentic_graph.py

from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import Tool

# Core Nodes
from Nodes.input_node import input_node
from Nodes.context_resolver import context_resolver_node
from Nodes.Query_expander import query_expander_node
from Nodes.intent_router_node import intent_router_node
from Nodes.response_node import response_node

# Tool Nodes
from Nodes.Tools.quiz_generator_node import quiz_generator_node
from Nodes.Tools.answer_key_node import answer_key_node
from Nodes.Tools.batch_grade_quizzes_node import batch_grade_quizzes_node
from Nodes.Tools.grade_single_quiz_node import grade_single_quiz_node
from Nodes.Tools.feedback_node import generate_feedback_node
from Nodes.Tools.Progress_node import progress_tracker_node
from Nodes.Tools.Rag_chat_node import rag_chat_node
from Nodes.Tools.revision_kit_node import revision_kit_node
from Nodes.Tools.notifier_node import notifier_node
from Nodes.Tools.planner_node import planner_node

# === ✅ FIXED Tool Wrapper ===
def wrap_tool(tool_fn: Tool) -> RunnableLambda:
    return RunnableLambda(lambda state: tool_fn.invoke(**state["tool_args"]))

# === Multi-Quiz Controller Node ===
def multi_quiz_controller_node() -> RunnableLambda:
    def control(state):
        count = state.get("quiz_count", 0)
        max_count = state.get("max_quizzes", 1)
        if count < max_count:
            state["quiz_count"] = count + 1
            state["tool_name"] = "quiz_generator_node"
        else:
            state["tool_name"] = "multi_quiz_complete"
        return state
    return RunnableLambda(control)

# === Grade Chain Router Node ===
def grade_chain_router_node() -> RunnableLambda:
    def route(state):
        if state.get("skip_feedback"):
            return "skip_to_notifier"
        if state.get("score", 100) < 40:
            return "rescue_needed"
        return "normal_feedback"
    return RunnableLambda(route)

# === Build Agentic LangGraph ===
def build_agentic_graph():
    builder = StateGraph(dict)

    # Core Nodes
    builder.add_node("input_node", input_node())
    builder.add_node("context_resolver_node", context_resolver_node())
    builder.add_node("query_expander_node", query_expander_node())
    builder.add_node("intent_router_node", intent_router_node())
    builder.add_node("response_node", response_node)

    # Wrapped Tool Nodes
    builder.add_node("quiz_generator_node", wrap_tool(quiz_generator_node))
    builder.add_node("grade_single_quiz_node", wrap_tool(grade_single_quiz_node))
    builder.add_node("batch_grade_quizzes_node", wrap_tool(batch_grade_quizzes_node))
    builder.add_node("generate_feedback_node", wrap_tool(generate_feedback_node))
    builder.add_node("planner_node", wrap_tool(planner_node))
    builder.add_node("notifier_node", wrap_tool(notifier_node))
    builder.add_node("answer_key_node", wrap_tool(answer_key_node))
    builder.add_node("progress_tracker_node", wrap_tool(progress_tracker_node))
    builder.add_node("rag_chat_node", wrap_tool(rag_chat_node))
    builder.add_node("revision_kit_node", wrap_tool(revision_kit_node))

    # Control Nodes
    builder.add_node("multi_quiz_controller_node", multi_quiz_controller_node())
    grade_router = grade_chain_router_node()
    builder.add_node("grade_chain_router_node", grade_router)

    # Flow Logic
    builder.set_entry_point("input_node")
    builder.add_edge("input_node", "context_resolver_node")
    builder.add_edge("context_resolver_node", "query_expander_node")
    builder.add_edge("query_expander_node", "intent_router_node")

    builder.add_conditional_edges(
        "intent_router_node",
        lambda state: state.get("tool_name", ""),
        {
            "quiz_generator_node": "quiz_generator_node",
            "multi_quiz_controller_node": "multi_quiz_controller_node",
            "grade_single_quiz_node": "grade_single_quiz_node",
            "batch_grade_quizzes_node": "batch_grade_quizzes_node",
            "generate_feedback_node": "generate_feedback_node",
            "planner_node": "planner_node",
            "notifier_node": "notifier_node",
            "answer_key_node": "answer_key_node",
            "progress_tracker_node": "progress_tracker_node",
            "rag_chat_node": "rag_chat_node",
            "revision_kit_node": "revision_kit_node",
            "unknown": "response_node"
        }
    )

    # Multi-Quiz Flow
    builder.add_edge("multi_quiz_controller_node", "quiz_generator_node")
    builder.add_edge("quiz_generator_node", "multi_quiz_controller_node")
    builder.add_conditional_edges(
        "multi_quiz_controller_node",
        lambda s: s.get("tool_name"),
        {
            "quiz_generator_node": "quiz_generator_node",
            "multi_quiz_complete": "response_node"
        }
    )

    # Grade Feedback Flow
    builder.add_edge("grade_single_quiz_node", "grade_chain_router_node")
    builder.add_conditional_edges(
        "grade_chain_router_node",
        lambda s: grade_router.invoke(s),
        {
            "skip_to_notifier": "notifier_node",
            "rescue_needed": "revision_kit_node",
            "normal_feedback": "generate_feedback_node"
        }
    )
    builder.add_edge("revision_kit_node", "notifier_node")
    builder.add_edge("notifier_node", "progress_tracker_node")
    builder.add_edge("progress_tracker_node", "response_node")
    builder.add_edge("generate_feedback_node", "notifier_node")

    # Batch Grade
    builder.add_edge("batch_grade_quizzes_node", "progress_tracker_node")

    # Study Plan Flow
    builder.add_edge("planner_node", "quiz_generator_node")
    builder.add_edge("planner_node", "notifier_node")
    builder.add_edge("quiz_generator_node", "response_node")
    builder.add_edge("notifier_node", "response_node")

    # Quiz → Answer Key → Response
    builder.add_edge("quiz_generator_node", "answer_key_node")
    builder.add_edge("answer_key_node", "response_node")

    # Progress → Notifier → Response
    builder.add_edge("progress_tracker_node", "notifier_node")
    builder.add_edge("notifier_node", "response_node")

    # Direct Tool → Response
    builder.add_edge("generate_feedback_node", "response_node")
    builder.add_edge("answer_key_node", "response_node")
    builder.add_edge("rag_chat_node", "response_node")
    builder.add_edge("revision_kit_node", "response_node")

    # Final Node
    builder.set_finish_point("response_node")

    return builder.compile()
