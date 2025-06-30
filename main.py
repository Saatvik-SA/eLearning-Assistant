# --- main.py ---

import os
from dotenv import load_dotenv

from Utilities.Embeddings import get_embedder
from Utilities.ChromaDB import add_chunks_to_chromadb, get_all_chromadb_chunks, query_chromadb_for_context, get_chromadb_collection
from Utilities.PDF import extract_text_from_uploaded_files

from Agents.Planner_agent import run_study_planner, export_study_plan_to_excel
from Agents.Quiz_generator import run_quiz_generator, export_quiz_to_pdf
from Agents.Quiz_grader import run_grader, export_graded_report_to_pdf
from Agents.AnswerKey import run_answer_key_generator
from Agents.Rag_chat import run_rag_chat

import fitz
import pandas as pd

# --- Load API Key ---
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env")

# --- Step 1: Load and Embed PDFs ---
def process_pdfs_from_folder(folder_path="Data/Upload"):
    all_chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            with fitz.open(pdf_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
                all_chunks.append(text)
    return all_chunks

def embed_and_store_chunks(chunks):
    embedder = get_embedder()
    chunk_embeddings = embedder.encode(chunks, show_progress_bar=True)
    add_chunks_to_chromadb(chunks, chunk_embeddings)
    return embedder

# --- CLI Menu ---
def main():
    print("\n===== eLearning Agent System =====")
    print("1. Generate Study Plan")
    print("2. Generate Quiz")
    print("3. Grade Student Answer Sheet")
    print("4. Generate Answer Key")
    print("5. Ask a Question (RAG Chat)")
    print("6. Exit")

    choice = input("Choose an option: ").strip()

    # Step 2: Load PDFs and process if needed
    chunks = process_pdfs_from_folder()
    embedder = embed_and_store_chunks(chunks)
    collection = get_chromadb_collection()
    total_chunks = len(get_all_chromadb_chunks())

    if choice == "1":
        weeks = int(input("Enter number of weeks before the exam: "))
        plan = run_study_planner(collection, total_chunks, weeks)
        export_study_plan_to_excel(plan, "Data/Output/Study_Plan.xlsx")

    elif choice == "2":
        quiz = run_quiz_generator(collection, total_chunks)
        export_quiz_to_pdf(quiz, "Data/Output/Generated_Quiz.pdf")

    elif choice == "3":
        path = input("Enter path to student answer PDF (e.g., Data/Upload/answers.pdf): ").strip()
        quiz = run_quiz_generator(collection, total_chunks)
        graded = run_grader(quiz, path)
        export_graded_report_to_pdf(graded, "Data/Output/Student_Graded_Report.pdf")

    elif choice == "4":
        quiz = run_quiz_generator(collection, total_chunks)
        run_answer_key_generator(quiz, filename="Data/Output/Generated_Answer_Key.pdf")

    elif choice == "5":
        run_rag_chat(embedder, collection)

    elif choice == "6":
        print("Exiting...")

    else:
        print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
