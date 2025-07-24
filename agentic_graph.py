# agentic_graph.py

from langgraph.graph import StateGraph
from Nodes.input_node import input_node
from Nodes.context_resolver import context_resolver_node
from Nodes.Query_expander import agentic_query_expander_node
from Nodes.intent_router_node import intent_router_node
from Nodes.response_node import response_node
from Nodes.Tools.planner_node import planner_node
from Nodes.Tools.quiz_generator_node import quiz_generator_node
from Nodes.Tools.answer_key_node import answer_key_node
from Nodes.Tools.revision_kit_node import revision_kit_node_wrapper
from Nodes.Tools.grade_single_quiz_node import grade_single_quiz_node_wrapper
from Nodes.Tools.batch_grade_quizzes_node import batch_grade_quizzes_node_wrapper
from Nodes.Tools.feedback_node import feedback_node_wrapper
from Nodes.Tools.Progress_node import progress_node_wrapper
from Nodes.Tools.notifier_node import notifier_node_wrapper
from Nodes.Tools.Rag_chat_node import rag_chat_node_wrapper

def build_agentic_graph():
    builder = StateGraph(dict)
    # Core Nodes
    builder.add_node("input_node", input_node())
    builder.add_node("context_resolver_node", context_resolver_node())
    builder.add_node("query_expander_node", agentic_query_expander_node())
    builder.add_node("intent_router_node", intent_router_node())
    builder.add_node("planner_node", planner_node())
    builder.add_node("quiz_generator_node", quiz_generator_node())
    builder.add_node("answer_key_node", answer_key_node())
    builder.add_node("revision_kit_node", revision_kit_node_wrapper())
    builder.add_node("grade_single_quiz_node", grade_single_quiz_node_wrapper())
    builder.add_node("batch_grade_quizzes_node", batch_grade_quizzes_node_wrapper())
    builder.add_node("feedback_node", feedback_node_wrapper())
    builder.add_node("progress_node", progress_node_wrapper())
    builder.add_node("notifier_node", notifier_node_wrapper())
    builder.add_node("rag_chat_node", rag_chat_node_wrapper())
    builder.add_node("response_node", response_node())
    # Flow Logic for all intents
    builder.set_entry_point("input_node")
    builder.add_edge("input_node", "context_resolver_node")
    builder.add_edge("context_resolver_node", "query_expander_node")
    builder.add_edge("query_expander_node", "intent_router_node")
    builder.add_conditional_edges(
        "intent_router_node",
        lambda state: state.get("tool_name"),
        {
            "planner_node": "planner_node",
            "quiz_generator_node": "quiz_generator_node",
            "answer_key_node": "answer_key_node",
            "revision_kit_node": "revision_kit_node",
            "grade_single_quiz_node": "grade_single_quiz_node",
            "batch_grade_quizzes_node": "batch_grade_quizzes_node",
            "feedback_node": "feedback_node",
            "progress_node": "progress_node",
            "notifier_node": "notifier_node",
            "rag_chat_node": "rag_chat_node"
        }
    )
    builder.add_edge("planner_node", "response_node")
    builder.add_edge("quiz_generator_node", "response_node")
    builder.add_edge("answer_key_node", "response_node")
    builder.add_edge("revision_kit_node", "response_node")
    builder.add_edge("batch_grade_quizzes_node", "response_node")
    builder.add_edge("feedback_node", "response_node")
    builder.add_edge("progress_node", "response_node")
    builder.add_edge("notifier_node", "response_node")
    builder.add_edge("rag_chat_node", "response_node")
    builder.set_finish_point("response_node")
    return builder.compile()
