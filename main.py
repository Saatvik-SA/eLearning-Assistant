# --- File: main.py (trial2 with Gemini-safe multi-intent parsing) ---

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from tkinter import filedialog, Tk
import fitz

from Utilities.Embeddings import get_embedder
from Utilities.ChromaDB import add_chunks_to_chromadb, get_chromadb_collection
from Agents.Planner_agent import run_study_planner, export_study_plan_to_excel
from Agents.Quiz_generator import run_quiz_generator, export_quiz_to_pdf
from Agents.Quiz_grader import run_grader, export_graded_report_to_pdf
from Agents.AnswerKey import run_answer_key_generator
from Agents.Rag_chat import run_rag_chat

# === Load API Key ===
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# === Upload PDFs ===
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

# === Load + Embed PDFs ===
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

# === Gemini Multi-Intent Classifier ===
def classify_intent(user_input):
    prompt = ChatPromptTemplate.from_template("""
You are an AI router for an educational assistant.

From the user's request, extract the names of ALL tools to be executed.

Tool options:
- study_planner
- quiz_generator
- answer_key
- grader
- rag_chat

Return a plain Python list like: ["quiz_generator", "answer_key"]
Do NOT explain anything else. Only return the list.

User: {user_input}
""")
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    formatted = prompt.format_messages(user_input=user_input)
    result = model.invoke(formatted).content.strip()

    # Safe parsing
    if result.startswith("[") and result.endswith("]"):
        try:
            parsed = eval(result)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

    # Fallback: detect single tool
    for keyword in ["study_planner", "quiz_generator", "answer_key", "grader", "rag_chat"]:
        if keyword in result:
            return [keyword]

    print("Could not parse Gemini response:", result)
    return []

# === Multi-Agent Executor ===
def run_agentic_action(user_input, collection, embedder, total_chunks):
    actions = classify_intent(user_input)
    if not actions:
        print("No valid actions identified.")
        return

    for action in actions:
        if action == "study_planner":
            weeks = None
            for word in user_input.split():
                if word.isdigit():
                    weeks = int(word)
            if not weeks:
                weeks = int(input("How many weeks until the exam? "))
            plan = run_study_planner(collection, total_chunks, weeks)
            export_study_plan_to_excel(plan, "Data/Output/study_plan.xlsx")
            print("Study plan created and saved.\n")

        elif action == "quiz_generator":
            quiz = run_quiz_generator(collection, total_chunks)
            export_quiz_to_pdf(quiz, "Data/Output/Generated_Quiz.pdf")
            print("Quiz saved.\n")

        elif action == "answer_key":
            quiz = run_quiz_generator(collection, total_chunks)
            run_answer_key_generator(quiz, "Data/Output/Answer_Key.pdf")
            print("Answer key saved.\n")

        elif action == "grader":
            student_pdf = filedialog.askopenfilename(title="Select student answer sheet PDF")
            quiz = run_quiz_generator(collection, total_chunks)
            graded = run_grader(quiz, student_pdf)
            export_graded_report_to_pdf(graded, "Data/Output/Graded_Report.pdf")
            print("Grading complete.\n")

        elif action == "rag_chat":
            run_rag_chat(embedder, collection)

        else:
            print(f"Unknown action: {action}")

# === Main Runner ===
if __name__ == "__main__":
    print("Upload academic PDFs to begin.")
    upload_pdfs()

    chunks = load_and_chunk_pdfs()
    total_chunks = len(chunks)
    collection, embedder = embed_and_store_chunks(chunks)

    print("\nType your request: \n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        run_agentic_action(user_input, collection, embedder, total_chunks)
