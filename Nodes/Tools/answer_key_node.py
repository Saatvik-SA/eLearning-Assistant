# Tools/answer_key_node.py

from langchain_core.tools import tool
from Agents.AnswerKey import run_answer_key_generator

@tool
def answer_key_node() -> str:
    """
    Generates an answer key from a quiz file (with 'quiz' in its name) found in 'Data/Upload',
    using textbook context embedded from the same folder.
    The generated answer key is saved as a PDF in 'Data/Output'.
    
    This tool supports both .pdf and .txt quiz formats.
    It uses embedded textbook context to ensure answers are accurate.
    
    Returns:
        str: Message indicating the file path of the generated answer key.
    """
    run_answer_key_generator()
    return "Answer key has been generated and saved in Data/Output."
