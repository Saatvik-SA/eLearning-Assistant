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
        lambda state: _intent_router_conditional(state),
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
    # Remove the conditional edge for grading, as intent router now handles it
    # builder.add_conditional_edges(
    #     "grade_single_quiz_node",
    #     lambda state: _determine_grading_type(state),
    #     {
    #         "single": "response_node",
    #         "batch": "batch_grade_quizzes_node"
    #     }
    # )
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

def _intent_router_conditional(state):
    tool_name = state.get("tool_name", "")
    if tool_name == "grade_single_quiz_node" or tool_name == "batch_grade_quizzes_node":
        # For grading, check number of files in Data/Answers
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
    return tool_name

def _determine_grading_type(state):
    """
    Intelligently determines grading type based on actual number of answer sheets in Data/Answers.
    Overrides LLM's grading_type constraint if needed.
    """
    import os
    import logging
    
    # Count answer sheets in Data/Answers
    answers_dir = "Data/Answers"
    if os.path.exists(answers_dir):
        answer_files = [f for f in os.listdir(answers_dir) if f.lower().endswith('.pdf')]
        num_files = len(answer_files)
        logging.info(f"[Grading Type Detection] Found {num_files} answer files in {answers_dir}: {answer_files}")
    else:
        num_files = 0
        logging.info(f"[Grading Type Detection] No {answers_dir} directory found")
    
    # If multiple files, force batch grading regardless of LLM's classification
    if num_files > 1:
        logging.info(f"[Grading Type Detection] Multiple files detected ({num_files}), routing to BATCH grading")
        return "batch"
    else:
        logging.info(f"[Grading Type Detection] Single file or no files detected ({num_files}), routing to SINGLE grading")
        return "single"
