from typing import Any, Dict, List, Sequence, TypedDict, Optional
from langchain_core.messages import BaseMessage

class RequestContextState(TypedDict, total=False):
    # Extend as needed for request context
    user_id: Optional[str]
    session_id: Optional[str]
    timestamp: Optional[str]
    # Add more fields as required

class AgentState(TypedDict, total=False):
    """
    Represents the state of the agentic graph at any point in the workflow.

    Attributes:
        messages: List of all messages in the conversation (user and assistant)
        most_recent_question: The last question asked by the user
        intent: The classified intent for the current query
        request_context: Contextual metadata for the request/session
        modified_recent_message: The most recent message after any modifications/expansions
        additional_source: List of additional data sources referenced
        tool_call_completed: Whether the tool/agent call has completed
        image_chunk_map: Mapping for any image chunking (if used)
        textbook: Name or path of the textbook/reference document
        collection: Embedded document collection (ChromaDB)
        embedder: Embedding model instance
        total_chunks: Number of chunks in the context
        error: Error message, if any
        files: List of output files generated
        response: Final response string
        tool: Name of the tool/agent used
        status: Status of the workflow (e.g., 'done', 'error')
    """
    messages: Sequence[BaseMessage]
    most_recent_question: str
    intent: str
    request_context: RequestContextState
    modified_recent_message: str
    additional_source: List[str]
    tool_call_completed: bool
    image_chunk_map: Dict[str, Any]
    textbook: Optional[str]
    collection: Any
    embedder: Any
    total_chunks: Optional[int]
    error: Optional[str]
    files: Optional[List[str]]
    response: Optional[str]
    tool: Optional[str]
    status: Optional[str]

def update_agent_state(state: AgentState, **kwargs) -> AgentState:
    """
    Returns a new AgentState with updated fields.
    """
    updated_state_dict = {**state, **kwargs}
    return AgentState(**updated_state_dict) 