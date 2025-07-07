# --- main.py ---

import os
from dotenv import load_dotenv

from Utilities.Core import (
    upload_study_pdfs,
    upload_answer_pdfs,
    select_pdf_file,
    prepare_academic_context
)

from Agents.Planner_agent import run_study_planner, export_study_plan_to_excel
from Agents.Quiz_generator import run_quiz_generator, export_quiz_to_pdf
from Agents.Quiz_grader import run_grader, export_graded_report_to_pdf, batch_grade_all_answers
from Agents.AnswerKey import run_answer_key_generator
from Agents.Rag_chat import run_rag_chat
from Agents.Feedback_agent import run_feedback_agent
from Agents.Rescue_agent import run_rescue_agent
from Agents.Progress_tracker import track_progress


# === Load API Key ===
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


# === Intent-Based Router ===
def agentic_router(user_input):
    user_input = user_input.lower()

    # Prepare academic context once per session
    chunks_uploaded = prepare_academic_context()
    collection, embedder, total_chunks = chunks_uploaded

    if "study plan" in user_input or "planner" in user_input:
        weeks = extract_weeks(user_input)
        plan = run_study_planner(collection, total_chunks, weeks)
        export_study_plan_to_excel(plan, filename="Data/Output/study_plan.xlsx")

    elif "quiz" in user_input:
        quiz = run_quiz_generator(collection, total_chunks)
        export_quiz_to_pdf(quiz, filename="Data/Output/Generated_Quiz.pdf")

    elif "batch grade" in user_input or "grade all" in user_input:
        quiz = run_quiz_generator(collection, total_chunks)
        batch_grade_all_answers()

    elif "grade" in user_input or "mark" in user_input:
        student_pdf = select_pdf_file("Select student answer sheet PDF")
        quiz = run_quiz_generator(collection, total_chunks)
        graded = run_grader(quiz, student_pdf)

        graded_path = "Data/Output/Student_Graded_Report.pdf"
        export_graded_report_to_pdf(graded, filename=graded_path)

        feedback_choice = input("Do you want feedback on this paper? (yes/no): ").strip().lower()
        if feedback_choice in {"yes", "y"}:
            feedback_path = "Data/Output/Student_Feedback_Report.pdf"
            run_feedback_agent(graded, filename=feedback_path)

    elif "answer key" in user_input:
        quiz = run_quiz_generator(collection, total_chunks)
        run_answer_key_generator(quiz, filename="Data/Output/Answer_Key.pdf")

    elif "feedback" in user_input:
        graded_file = select_pdf_file("Select Graded Report to generate Feedback")
        with open(graded_file, "r", encoding="utf-8", errors="ignore") as f:
            graded_text = f.read()
        run_feedback_agent(graded_text, filename="Data/Output/Student_Feedback_Report.pdf")

    elif "revision" in user_input or "rescue" in user_input or "exam tomorrow" in user_input:
        run_rescue_agent(collection, total_chunks)

    elif "progress" in user_input or "track" in user_input:
        track_progress()

    else:
        run_rag_chat(embedder, collection)


# === Week Extractor ===
def extract_weeks(user_input):
    for word in user_input.split():
        if word.isdigit():
            return int(word)
    return int(input("How many weeks until the exam? "))


# === Entry Point ===
if __name__ == "__main__":
    print("Upload your academic PDFs...")
    upload_study_pdfs()

    print("\neLearning Assistant is ready!")
    print("Ask me to do something like:")
    print("➡  create study plan")
    print("➡  generate quiz")
    print("➡  grade answers / batch grade")
    print("➡  answer key / feedback / revision / progress")
    print("➡  or ask any academic question\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        agentic_router(user_input)
