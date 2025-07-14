# main.py

import os
from dotenv import load_dotenv
from Utilities.Core import upload_study_pdfs, upload_answer_pdfs
from agentic_graph import build_agentic_graph

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
    print("=== eLearning Assistant ===")
    
    # === Upload Study Material ===
    print("Upload academic study materials (PDFs)...")
    upload_study_pdfs()
    uploaded_files = get_uploaded_files()

    # === Upload Answer Sheets ===
    if input("Upload answer sheets for grading? (yes/no): ").strip().lower() in {"yes", "y"}:
        upload_answer_pdfs()
    else:
        print("Skipping answer upload.")

    # === Load LangGraph ===
    graph = build_agentic_graph()

    # === Main Loop ===
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Session ended.")
            break

        # === Prepare Input ===
        data = {
            "input": user_input,
            "uploaded_files": uploaded_files
        }

        # === Invoke Graph ===
        try:
            result = graph.invoke(data)

            print("\n=== Response ===")
            print(result["response"])
            if result.get("files"):
                print("Generated Files:")
                for f in result["files"]:
                    print("→", f)

        except Exception as e:
            print(f"[Error] {str(e)}")


if __name__ == "__main__":
    main()
