# --- File: main.py ---

import os
from dotenv import load_dotenv
from tkinter import filedialog, Tk
import fitz

from Utilities.Embeddings import get_embedder
from Utilities.ChromaDB import add_chunks_to_chromadb, get_chromadb_collection
from Agents.Planner_agent import run_study_planner, export_study_plan_to_excel
from Agents.Quiz_generator import run_quiz_generator, export_quiz_to_pdf
from Agents.Quiz_grader import run_grader, export_graded_report_to_pdf
from Agents.AnswerKey import run_answer_key_generator
from Agents.Rag_chat import run_rag_chat
from Agents.Feedback_agent import run_feedback_agent

# === Load API Key ===
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


# === Upload PDFs via Dialog ===
def upload_pdfs():
    root = Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)

    files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    upload_dir = "Data/Upload"
    os.makedirs(upload_dir, exist_ok=True)

    for file_path in files:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(upload_dir, file_name)
        with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())
        print(f"Uploaded: {file_name}")

    root.destroy()


# === Select PDF Dialog Utility ===
def select_pdf_file(title="Select PDF file"):
    root = Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_path = filedialog.askopenfilename(title=title, filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    return file_path


# === Chunk + Embed PDFs ===
def load_and_chunk_pdfs():
    folder = "Data/Upload"
    all_texts = []

    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            with fitz.open(os.path.join(folder, file)) as doc:
                text = "".join([page.get_text() for page in doc])
                all_texts.append(text)

    return all_texts


def embed_and_store_chunks(chunks):
    embedder = get_embedder()
    embeddings = embedder.encode(chunks, show_progress_bar=True)
    add_chunks_to_chromadb(chunks, embeddings)
    return get_chromadb_collection(), embedder


# === Intent-based Router ===
def agentic_router(user_input):
    user_input = user_input.lower()

    chunks = load_and_chunk_pdfs()
    total_chunks = len(chunks)
    collection, embedder = embed_and_store_chunks(chunks)

    if "study plan" in user_input or "planner" in user_input:
        weeks = None
        for word in user_input.split():
            if word.isdigit():
                weeks = int(word)
                break
        if not weeks:
            weeks = int(input("How many weeks until the exam? "))
        plan = run_study_planner(collection, total_chunks, weeks)
        export_study_plan_to_excel(plan, filename="Data/Output/study_plan.xlsx")

    elif "quiz" in user_input:
        quiz = run_quiz_generator(collection, total_chunks)
        export_quiz_to_pdf(quiz, filename="Data/Output/Generated_Quiz.pdf")

    elif "grade" in user_input or "mark" in user_input:
        student_pdf = select_pdf_file("Select student answer sheet PDF")
        quiz = run_quiz_generator(collection, total_chunks)
        graded = run_grader(quiz, student_pdf)

        graded_path = "Data/Output/Student_Graded_Report.pdf"
        export_graded_report_to_pdf(graded, filename=graded_path)
        print(f"Graded report saved to: {graded_path}")

        feedback_choice = input("Do you want feedback on this paper? (yes/no): ").strip().lower()
        if feedback_choice in {"yes", "y"}:
            feedback_path = "Data/Output/Student_Feedback_Report.pdf"
            run_feedback_agent(graded, filename=feedback_path)
            print(f"Feedback report saved to: {feedback_path}")

    elif "answer key" in user_input:
        quiz = run_quiz_generator(collection, total_chunks)
        run_answer_key_generator(quiz, filename="Data/Output/Answer_Key.pdf")

    elif "feedback" in user_input:
        graded_file = select_pdf_file("Select Graded Report to generate Feedback")
        with open(graded_file, "r") as f:
            graded_text = f.read()
        run_feedback_agent(graded_text, filename="Data/Output/Student_Feedback_Report.pdf")

    else:
        run_rag_chat(embedder, collection)


# === Entry ===
if __name__ == "__main__":
    print("Upload your academic PDFs...")
    upload_pdfs()

    print("\neLearning Assistant is ready!")
    print("Ask me to do something (e.g., 'create study plan', 'grade answers', 'generate quiz', 'give answer key', 'feedback' or ask a question)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        agentic_router(user_input)
