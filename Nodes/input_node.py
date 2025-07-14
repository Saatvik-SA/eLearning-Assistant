# nodes/input_node.py
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage

def input_node() -> RunnableLambda:
    """
   Captures user input and list of uploaded file paths.
    
    Args:
        user_input (str): User's text query (e.g., a question, command).
        uploaded_files (list[str]): Paths to files uploaded by the user (optional).

    Returns:
        dict: {
            "query": user_input,
            "uploaded_files": uploaded_files or []
        }
    """
    def format_input(x):
        return {
            "query": x["input"].strip(),
            "uploaded_files": x.get("uploaded_files", []),
            "message": HumanMessage(content=x["input"].strip())
        }

    return RunnableLambda(format_input)