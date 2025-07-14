from langchain_core.tools import tool
from Agents.Rescue_agent import run_rescue_agent
from Utilities.Core import prepare_academic_context

@tool
def revision_kit_node(inputs: dict = {}) -> dict:
    """
    Generates a revision kit for last-minute exam preparation using the uploaded academic content.

    Output:
    {
        "status": "success",
        "file_path": "Data/Output/Revision_Kit.pdf",
        "output_type": "file"
    }
    """
    # Prepare embedded academic context
    collection, embedder, total_chunks = prepare_academic_context()

    # Run the rescue agent (saves PDF internally)
    run_rescue_agent(collection, total_chunks)

    return {
        "status": "success",
        "file_path": "Data/Output/Revision_Kit.pdf",
        "output_type": "file"
    }
