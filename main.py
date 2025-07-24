# main.py

import os
import logging
from dotenv import load_dotenv
from Utilities.Core import upload_study_pdfs, upload_answer_pdfs, list_pdfs_in_directory, prompt_user_to_select_file
from agentic_graph import build_agentic_graph
from Nodes.input_node import input_node
from Nodes.context_resolver import context_resolver_node
from Nodes.Query_expander import agentic_query_expander_node

# === Advanced Logging Setup ===
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/elearning.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# === Setup ===
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def get_uploaded_files():
    """
    Lists all PDF files currently in Data/Upload directory.
    """
    upload_dir = "Data/Upload"
    if not os.path.exists(upload_dir):
        return []
    return [
        os.path.join(upload_dir, f)
        for f in os.listdir(upload_dir)
        if f.lower().endswith(".pdf")
    ]

def main():
    print("=== eLearning Assistant (Study Plan, Quiz, Answer Key, Revision Kit & Quiz Grading) ===")
    logging.info("Started eLearning Assistant (Study Plan, Quiz, Answer Key, Revision Kit & Quiz Grading) mode.")
    print("Upload academic study materials (PDFs)...")
    upload_study_pdfs()
    uploaded_files = get_uploaded_files()
    logging.info(f"Uploaded files: {uploaded_files}")
    graph = build_agentic_graph()
    logging.info("LangGraph built and ready.")
    while True:
        user_input = input("\nEnter your request (e.g., 'create a study plan for 4 weeks', 'generate a hard quiz', 'make answer key for quiz 1', 'give me a revision kit for my exam', 'grade my quiz answers', 'grade all student answers', 'give feedback for my graded paper', 'show my progress', 'notify my parent', or 'ask a question about history') or 'exit' to quit: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Session ended.")
            logging.info("Session ended by user.")
            break
        data = {
            "input": user_input,
            "query": user_input,
            "uploaded_files": uploaded_files
        }
        try:
            result = graph.invoke(data)
            print("\n=== Response ===")
            if result.get("status") == "awaiting_upload" and result.get("clarification_required"):
                print(result.get("response", "Please upload the student answer sheet PDF you want to grade."))
                if input("Upload answer sheets for grading? (yes/no): ").strip().lower() in {"yes", "y"}:
                    uploaded = upload_answer_pdfs()
                    if uploaded:
                        dest_path = uploaded[-1]
                        print(f"Uploaded: {os.path.basename(dest_path)} → {dest_path}")
                        data["file_reference"] = dest_path
                        result = graph.invoke(data)
                    else:
                        print("No file uploaded. Please try again.")
                else:
                    print("No answer sheet uploaded. Grading cancelled.")
            if result.get("error"):
                print(f"[Error] {result.get('error')}")
            else:
                print(result.get("response", "Done."))
            if result.get("files"):
                print("Generated Files:")
                for f in result["files"]:
                    print(f"→ {f}")
        except Exception as e:
            print(f"[Error] {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
