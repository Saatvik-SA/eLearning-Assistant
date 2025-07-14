# Tools/quiz_generator_node.py

from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from Agents.Quiz_generator import run_quiz_generator, export_quiz_to_pdf

class QuizGeneratorInput(BaseModel):
    collection: object = Field(..., description="ChromaDB vector store of academic content.")
    total_chunks: int = Field(..., description="Number of content chunks to use.")
    num_mcq: Optional[int] = Field(3, description="Number of MCQs.")
    num_short: Optional[int] = Field(2, description="Number of short answer questions.")
    num_long: Optional[int] = Field(2, description="Number of long answer questions.")
    num_fill: Optional[int] = Field(2, description="Number of fill in the blanks.")
    num_tf: Optional[int] = Field(2, description="Number of true/false questions.")
    difficulty: Optional[str] = Field(None, description="Difficulty level (easy, medium, hard).")

@tool(args_schema=QuizGeneratorInput)
def quiz_generator_node(inputs: QuizGeneratorInput) -> dict:
    """
    Wraps the quiz generator agent. Uses embedded academic content to generate a quiz.
    """
    print(f"[Quiz Generator Node] Running quiz generation...")

    quiz = run_quiz_generator(
        collection=inputs.collection,
        total_chunks=inputs.total_chunks,
        num_mcq=inputs.num_mcq,
        num_short=inputs.num_short,
        num_long=inputs.num_long,
        num_fill=inputs.num_fill,
        num_tf=inputs.num_tf,
        difficulty=inputs.difficulty
    )

    # Optional PDF export
    pdf_path = export_quiz_to_pdf(quiz)

    return {
        "status": "success",
        "quiz_preview": quiz[:300] + "...",
        "output_file": pdf_path
    }
