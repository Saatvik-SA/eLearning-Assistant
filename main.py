# --- main.py ---

import os
from dotenv import load_dotenv
from Utilities.Core import (
    upload_study_pdfs,
    upload_answer_pdfs,
    prepare_academic_context,
    select_pdf_file
)

from Agents.Planner_agent import run_study_planner, export_study_plan_to_excel
from Agents.Quiz_generator import run_quiz_generator, export_quiz_to_pdf
from Agents.Quiz_grader import run_grader, export_graded_report_to_pdf, batch_grade_all_answers
from Agents.AnswerKey import run_answer_key_generator
from Agents.Feedback_agent import run_feedback_agent
from Agents.Rescue_agent import run_rescue_agent
from Agents.Progress_tracker import track_progress
from Agents.Rag_chat import run_rag_chat
from Agents.Notifier_agent import run_parent_notifier


# === Load .env ===
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


# === Router ===
def agentic_router(user_input):
    user_input = user_input.lower()
    collection, embedder, total_chunks = prepare_academic_context()

    if "planner" in user_input or "study plan" in user_input:
        plan = run_study_planner(collection, total_chunks)  # Internally asks weeks
        export_study_plan_to_excel(plan)

    elif "quiz" in user_input:
        quiz = run_quiz_generator(collection, total_chunks)
        export_quiz_to_pdf(quiz)

    elif "batch grade" in user_input or "grade all" in user_input:
        batch_grade_all_answers()

    elif "grade" in user_input or "mark" in user_input:
        student_pdf = select_pdf_file("Select student answer sheet PDF")
        quiz = run_quiz_generator(collection, total_chunks)
        graded = run_grader(quiz, student_pdf)
        export_graded_report_to_pdf(graded)

        if input("Generate feedback? (yes/no): ").strip().lower() in {"yes", "y"}:
            run_feedback_agent(graded)

    elif "answer key" in user_input:
        quiz = run_quiz_generator(collection, total_chunks)
        run_answer_key_generator(quiz)

    elif "feedback" in user_input:
        graded_file = select_pdf_file("Select Graded Report to generate Feedback")
        with open(graded_file, "r", encoding="utf-8", errors="ignore") as f:
            graded_text = f.read()
        run_feedback_agent(graded_text)

    elif "revision" in user_input or "rescue" in user_input or "exam tomorrow" in user_input:
        run_rescue_agent(collection, total_chunks)

    elif "progress" in user_input or "track" in user_input:
        track_progress()

    elif "notify" in user_input or "parent" in user_input:
        run_parent_notifier()

    else:
        run_rag_chat(embedder, collection)


# === Entry ===
if __name__ == "__main__":
    print("Upload your academic study material PDFs:")
    upload_study_pdfs()

    upload_answers = input("Do you want to upload student answer sheets for grading? (yes/no): ").strip().lower()
    if upload_answers in {"yes", "y"}:
        upload_answer_pdfs()
    else:
        print("Skipping answer upload.")

    print("\neLearning Assistant Ready!")
    print("Try commands like: study plan, quiz, grade, batch grade, answer key, feedback, revision, progress, notify")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        agentic_router(user_input)
