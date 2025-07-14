# nodes/intent_router_node.py

from langchain_core.runnables import RunnableLambda

# === Intent to Tool Node Map ===
INTENT_TOOL_MAP = {
    "generate_quiz": "quiz_generator_node",
    "grade_quiz_single": "grade_single_quiz_node",
    "grade_quiz_batch": "batch_grade_quizzes_node",
    "generate_feedback": "generate_feedback_node",
    "create_answer_key": "answer_key_node",
    "track_progress": "progress_tracker_node",
    "generate_plan": "planner_node",
    "answer_question": "rag_chat_node",
    "revision_kit": "revision_kit_node",
    "notify_user": "notifier_node"
}

# === Acceptable Inputs for Each Tool ===
TOOL_ARG_FILTERS = {
    "quiz_generator_node": ["query", "collection", "total_chunks", "uploaded_files", "expanded"],
    "grade_single_quiz_node": ["query", "collection", "uploaded_files", "expanded"],
    "batch_grade_quizzes_node": ["query", "collection", "uploaded_files", "expanded"],
    "generate_feedback_node": ["query", "uploaded_files", "expanded"],
    "answer_key_node": ["query", "collection", "uploaded_files", "expanded"],
    "progress_tracker_node": ["query", "uploaded_files", "expanded"],
    "planner_node": ["query", "collection", "embedder", "total_chunks", "uploaded_files", "expanded"],
    "rag_chat_node": ["query", "collection", "expanded"],
    "revision_kit_node": ["query", "collection", "expanded"],
    "notifier_node": ["query", "uploaded_files", "expanded"]
}

def intent_router_node() -> RunnableLambda:
    def classify_and_route(inputs: dict) -> dict:
        expanded = inputs.get("expanded", {})
        intent = expanded.get("intent", "").strip()

        print(f"\nExtracted intent: {intent}")

        if not intent or intent not in INTENT_TOOL_MAP:
            raise ValueError(f"Unsupported or missing intent: {intent}")

        tool_name = INTENT_TOOL_MAP[intent]
        allowed_keys = TOOL_ARG_FILTERS.get(tool_name, [])

        # Filter only allowed args for the specific tool
        tool_args = {k: inputs[k] for k in allowed_keys if k in inputs}

        print(f"Routing to: {tool_name} for intent: {intent}")
        print(f"Tool Args: {list(tool_args.keys())}")

        return {
            **inputs,
            "intent": intent,
            "tool_name": tool_name,
            "confidence": 1.0,
            "tool_args": tool_args
        }

    return RunnableLambda(classify_and_route)
