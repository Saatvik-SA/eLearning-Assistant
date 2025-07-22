# main.py

import os
import logging
from dotenv import load_dotenv
from Utilities.Core import upload_study_pdfs, upload_answer_pdfs
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
    # === Upload Study Material ===
    print("Upload academic study materials (PDFs)...")
    upload_study_pdfs()
    uploaded_files = get_uploaded_files()
    logging.info(f"Uploaded files: {uploaded_files}")
    # === Load LangGraph ===
    graph = build_agentic_graph()
    logging.info("LangGraph built and ready.")
    # === Main Loop (Study Plan, Quiz, Answer Key, Revision Kit, Quiz Grading) ===
    while True:
        user_input = input("\nEnter your request (e.g., 'create a study plan for 4 weeks', 'generate a hard quiz', 'make answer key for quiz 1', 'give me a revision kit for my exam', 'grade my quiz answers', 'grade all student answers', 'give feedback for my graded paper', 'show my progress', 'notify my parent', or 'ask a question about history') or 'exit' to quit: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Session ended.")
            logging.info("Session ended by user.")
            break

        # Check if this is a batch grading request and prompt for answer files
        if any(indicator in user_input.lower() for indicator in ["batch", "all", "multiple", "several", "every"]) and "grade" in user_input.lower():
            print("\nFor batch grading, please ensure student answer PDFs are in the 'Data/Answers' folder.")
            print("The system will automatically grade all PDF files found there.")

        # === Prepare Input ===
        data = {
            "input": user_input,
            "query": user_input,
            "uploaded_files": uploaded_files
        }
        # === Standalone Feedback and Grading Flow ===
        answers_dir = "Data/Answers"
        output_dir = "Data/Output"
        existing_answers = [f for f in os.listdir(answers_dir) if f.lower().endswith(".pdf")] if os.path.exists(answers_dir) else []
        graded_reports = [f for f in os.listdir(output_dir) if f.lower().endswith("_graded.pdf")] if os.path.exists(output_dir) else []
        user_query_lower = user_input.lower()
        feedback_keywords = ["feedback", "review", "analyze", "marked"]
        wants_feedback = any(k in user_query_lower for k in feedback_keywords)
        wants_grading = "grade" in user_query_lower
        # --- Standalone Feedback ---
        if wants_feedback:
            # Debug: print all files in Data/Output
            output_files = os.listdir(output_dir) if os.path.exists(output_dir) else []
            print("[DEBUG] Files in Data/Output:", output_files)
            # Robust pattern: match any PDF containing 'Graded' (case-insensitive)
            graded_reports = [f for f in output_files if f.lower().endswith('.pdf') and 'graded' in f.lower()]
            if graded_reports:
                print("Multiple graded reports found:")
                for idx, fname in enumerate(graded_reports, 1):
                    print(f"{idx}. {fname}")
                sel = input("Select a graded report for feedback (number): ").strip()
                try:
                    sel_idx = int(sel) - 1
                    if 0 <= sel_idx < len(graded_reports):
                        data["graded_file_path"] = os.path.join(output_dir, graded_reports[sel_idx])
                        data["intent"] = "generate_feedback"
                        print(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {data['graded_file_path']}")
                        logging.info(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {data['graded_file_path']}")
                        result = graph.invoke(data)
                        # Print feedback result or file path
                        if result.get("status") == "success" and result.get("file_path"):
                            print(f"Feedback generated: {result['file_path']}")
                        else:
                            print("Feedback process completed. Check Data/Output for results.")
                        continue  # Ensure main loop continues after success
                    else:
                        print("Invalid selection. Feedback cancelled.")
                        continue
                except Exception:
                    print("Invalid input. Feedback cancelled.")
                    continue
            else:
                print("No graded reports found in Data/Output. Please upload a graded report (PDF) to get feedback.")
                uploaded = upload_answer_pdfs()
                if uploaded:
                    print("Uploaded files:")
                    for f in uploaded:
                        print(f"→ {f}")
                    # Use the most recently uploaded graded report
                    data["graded_file_path"] = uploaded[-1]
                    data["intent"] = "generate_feedback"
                    print(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {data['graded_file_path']}")
                    logging.info(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {data['graded_file_path']}")
                    result = graph.invoke(data)
                    # Print feedback result or file path
                    if result.get("status") == "success" and result.get("file_path"):
                        print(f"Feedback generated: {result['file_path']}")
                    else:
                        print("Feedback process completed. Check Data/Output for results.")
                    continue
                else:
                    print("No graded report uploaded. Feedback cancelled.")
                    continue
        # --- Standalone Grading ---
        elif wants_grading:
            if existing_answers:
                print(f"Found {len(existing_answers)} answer sheet(s) in Data/Answers:")
                for f in existing_answers:
                    print(f"→ {f}")
                use_existing = input("Use these for grading? (yes/no): ").strip().lower()
                if use_existing in {"yes", "y"}:
                    print("Proceeding with existing answer sheets.")
                    # Set file_reference for grading node
                    if len(existing_answers) == 1:
                        data["file_reference"] = os.path.join(answers_dir, existing_answers[0])
                    else:
                        sel = input("Select an answer sheet for grading (number): ").strip()
                        try:
                            sel_idx = int(sel) - 1
                            if 0 <= sel_idx < len(existing_answers):
                                data["file_reference"] = os.path.join(answers_dir, existing_answers[sel_idx])
                            else:
                                print("Invalid selection. Grading cancelled.")
                                continue
                        except Exception:
                            print("Invalid input. Grading cancelled.")
                            continue
                    data["intent"] = "generate_quiz_grade"
                    result = graph.invoke(data)
                    print("[DEBUG] Grading result:", result)
                    print("Grading complete.")
                    # Print graded report(s) and prompt for feedback
                    graded_files = []
                    if result.get("report_path"):
                        graded_files = [result["report_path"]]
                    elif result.get("report_paths"):
                        graded_files = result["report_paths"]
                    if graded_files:
                        print("Graded report(s):")
                        for idx, f in enumerate(graded_files, 1):
                            print(f"{idx}. {f}")
                        want_feedback = input("Would you like feedback on any graded report? (yes/no): ").strip().lower()
                        if want_feedback in {"yes", "y"}:
                            if len(graded_files) == 1:
                                feedback_file = graded_files[0]
                            else:
                                sel = input("Select a graded report for feedback (number): ").strip()
                                try:
                                    sel_idx = int(sel) - 1
                                    if 0 <= sel_idx < len(graded_files):
                                        feedback_file = graded_files[sel_idx]
                                    else:
                                        print("Invalid selection. Feedback cancelled.")
                                        continue
                                except Exception:
                                    print("Invalid input. Feedback cancelled.")
                                    continue
                            data_feedback = data.copy()
                            data_feedback["graded_file_path"] = feedback_file
                            data_feedback["intent"] = "generate_feedback"
                            print(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {feedback_file}")
                            logging.info(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {feedback_file}")
                            result_feedback = graph.invoke(data_feedback)
                            if result_feedback.get("status") == "success" and result_feedback.get("file_path"):
                                print(f"Feedback generated: {result_feedback['file_path']}")
                            else:
                                print("Feedback process completed. Check Data/Output for results.")
                            continue
                    continue
                else:
                    print("Please upload the student answer sheet PDF(s) you want to grade.")
                    uploaded = upload_answer_pdfs()
                    if uploaded:
                        print("Uploaded files:")
                        for f in uploaded:
                            print(f"→ {f}")
                        data["intent"] = "generate_quiz_grade"
                        result = graph.invoke(data)
                        print("[DEBUG] Grading result:", result)
                        print("Grading complete.")
                        # Print graded report(s) and prompt for feedback
                        graded_files = []
                        if result.get("report_path"):
                            graded_files = [result["report_path"]]
                        elif result.get("report_paths"):
                            graded_files = result["report_paths"]
                        if graded_files:
                            print("Graded report(s):")
                            for idx, f in enumerate(graded_files, 1):
                                print(f"{idx}. {f}")
                            want_feedback = input("Would you like feedback on any graded report? (yes/no): ").strip().lower()
                            if want_feedback in {"yes", "y"}:
                                if len(graded_files) == 1:
                                    feedback_file = graded_files[0]
                                else:
                                    sel = input("Select a graded report for feedback (number): ").strip()
                                    try:
                                        sel_idx = int(sel) - 1
                                        if 0 <= sel_idx < len(graded_files):
                                            feedback_file = graded_files[sel_idx]
                                        else:
                                            print("Invalid selection. Feedback cancelled.")
                                            continue
                                    except Exception:
                                        print("Invalid input. Feedback cancelled.")
                                        continue
                                data_feedback = data.copy()
                                data_feedback["graded_file_path"] = feedback_file
                                data_feedback["intent"] = "generate_feedback"
                                print(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {feedback_file}")
                                logging.info(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {feedback_file}")
                                result_feedback = graph.invoke(data_feedback)
                                if result_feedback.get("status") == "success" and result_feedback.get("file_path"):
                                    print(f"Feedback generated: {result_feedback['file_path']}")
                                else:
                                    print("Feedback process completed. Check Data/Output for results.")
                                continue
                        continue
                    else:
                        print("No answer sheets uploaded. Grading cancelled.")
                        continue
            else:
                print("No answer sheets found in Data/Answers. Please upload the student answer sheet PDF(s) you want to grade.")
                uploaded = upload_answer_pdfs()
                if uploaded:
                    print("Uploaded files:")
                    for f in uploaded:
                        print(f"→ {f}")
                    data["intent"] = "generate_quiz_grade"
                    result = graph.invoke(data)
                    print("[DEBUG] Grading result:", result)
                    print("Grading complete.")
                    # Print graded report(s) and prompt for feedback
                    graded_files = []
                    if result.get("report_path"):
                        graded_files = [result["report_path"]]
                    elif result.get("report_paths"):
                        graded_files = result["report_paths"]
                    if graded_files:
                        print("Graded report(s):")
                        for idx, f in enumerate(graded_files, 1):
                            print(f"{idx}. {f}")
                        want_feedback = input("Would you like feedback on any graded report? (yes/no): ").strip().lower()
                        if want_feedback in {"yes", "y"}:
                            if len(graded_files) == 1:
                                feedback_file = graded_files[0]
                            else:
                                sel = input("Select a graded report for feedback (number): ").strip()
                                try:
                                    sel_idx = int(sel) - 1
                                    if 0 <= sel_idx < len(graded_files):
                                        feedback_file = graded_files[sel_idx]
                                    else:
                                        print("Invalid selection. Feedback cancelled.")
                                        continue
                                except Exception:
                                    print("Invalid input. Feedback cancelled.")
                                    continue
                            data_feedback = data.copy()
                            data_feedback["graded_file_path"] = feedback_file
                            data_feedback["intent"] = "generate_feedback"
                            print(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {feedback_file}")
                            logging.info(f"[DEBUG] Invoking feedback with intent: generate_feedback, graded_file_path: {feedback_file}")
                            result_feedback = graph.invoke(data_feedback)
                            if result_feedback.get("status") == "success" and result_feedback.get("file_path"):
                                print(f"Feedback generated: {result_feedback['file_path']}")
                            else:
                                print("Feedback process completed. Check Data/Output for results.")
                            continue
                        continue
                    else:
                        print("No answer sheets uploaded. Grading cancelled.")
                        continue
        # --- Standalone Answer Key Generation ---
        elif "answer key" in user_query_lower or "generate answer key" in user_query_lower:
            upload_dir = "Data/Upload"
            quiz_files = [f for f in os.listdir(upload_dir) if "quiz" in f.lower() and f.lower().endswith((".pdf", ".txt"))] if os.path.exists(upload_dir) else []
            if quiz_files:
                print(f"Found {len(quiz_files)} quiz file(s) in Data/Upload:")
                for f in quiz_files:
                    print(f"→ {f}")
                use_existing = input("Use these for answer key generation? (yes/no): ").strip().lower()
                if use_existing in {"yes", "y"}:
                    print("Proceeding with existing quiz file(s).")
                    # Proceed to invoke the graph as usual
                    data["intent"] = "generate_answer_key"
                    result = graph.invoke(data)
                    print("[DEBUG] Answer key generation result:", result)
                    print("Answer key generation complete.")
                    continue
                else:
                    print("Please upload the quiz file (PDF or TXT) you want to use for answer key generation.")
                    uploaded = upload_study_pdfs()
                    if uploaded:
                        print("Uploaded files:")
                        for f in uploaded:
                            print(f"→ {f}")
                        data["intent"] = "generate_answer_key"
                        result = graph.invoke(data)
                        print("[DEBUG] Answer key generation result:", result)
                        print("Answer key generation complete.")
                        continue
                    else:
                        print("No quiz file uploaded. Answer key generation cancelled.")
                        continue
            else:
                print("No quiz file found in Data/Upload. Please upload the quiz file (PDF or TXT) you want to use for answer key generation.")
                uploaded = upload_study_pdfs()
                if uploaded:
                    print("Uploaded files:")
                    for f in uploaded:
                        print(f"→ {f}")
                    data["intent"] = "generate_answer_key"
                    result = graph.invoke(data)
                    print("[DEBUG] Answer key generation result:", result)
                    print("Answer key generation complete.")
                    continue
                else:
                    print("No quiz file uploaded. Answer key generation cancelled.")
                    continue
        # --- All other requests ---
        else:
            try:
                result = graph.invoke(data)
                print("\n=== Response ===")
                if result.get("status") == "awaiting_upload" and result.get("clarification_required"):
                    # Prompt user to upload answer sheet PDF using the utility
                    print(result.get("response", "Please upload the student answer sheet PDF you want to grade."))
                    if input("Upload answer sheets for grading? (yes/no): ").strip().lower() in {"yes", "y"}:
                        uploaded = upload_answer_pdfs()
                        if uploaded:
                            # Use the most recently uploaded answer sheet
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
