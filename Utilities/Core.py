# --- Utilities/Core.py ---
import os
from tkinter import filedialog, Tk
from Utilities.PDF import extract_texts_from_folder
from Utilities.Embeddings import get_embedder, get_chunk_embeddings
from Utilities.ChromaDB import add_chunks_to_chromadb, get_chromadb_collection

# === PDF Upload Dialogs ===
def upload_study_pdfs():
    """Upload academic content PDFs into Data/Upload."""
    return _upload_pdfs_to_folder("Data/Upload")

def upload_answer_pdfs():
    """Upload student answer sheets into Data/Answers, skipping duplicates."""
    return _upload_pdfs_to_folder_no_duplicates("Data/Answers")

def _upload_pdfs_to_folder(target_folder):
    """Generic function to upload PDFs to a given folder."""
    root = Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    os.makedirs(target_folder, exist_ok=True)
    saved = []
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(target_folder, file_name)
        with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())
        saved.append(dest_path)
        print(f"Uploaded: {file_name} → {target_folder}")
    return saved

def _upload_pdfs_to_folder_no_duplicates(target_folder):
    """Generic function to upload PDFs to a given folder, skipping duplicates."""
    from tkinter import filedialog, Tk
    import os
    root = Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    os.makedirs(target_folder, exist_ok=True)
    saved = []
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(target_folder, file_name)
        if os.path.exists(dest_path):
            print(f"{file_name} already exists in {target_folder}. Skipping upload.")
            continue
        with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())
        saved.append(dest_path)
        print(f"Uploaded: {file_name} → {target_folder}")
    return saved

def select_pdf_file(title="Select PDF file"):
    """Show file dialog and return selected PDF path."""
    root = Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_path = filedialog.askopenfilename(title=title, filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    return file_path

def list_pdfs_in_directory(directory):
    """Return a list of PDF file names in the given directory (not full paths)."""
    import os
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]


def prompt_user_to_select_file(files, prompt_message="Select a file (number):"):
    """Prompt the user to select a file from a list. Returns the selected file name or None."""
    if not files:
        return None
    for idx, fname in enumerate(files, 1):
        print(f"{idx}. {fname}")
    sel = input(prompt_message).strip()
    try:
        sel_idx = int(sel) - 1
        if 0 <= sel_idx < len(files):
            return files[sel_idx]
        else:
            print("Invalid selection.")
            return None
    except Exception:
        print("Invalid input.")
        return None

# === Academic Context Preparation Pipeline ===
def prepare_academic_context():
    """Loads and embeds study PDFs from Data/Upload. Returns (collection, embedder, total_chunks)."""
    chunks = extract_texts_from_folder("Data/Upload")
    total_chunks = len(chunks)
    embedder = get_embedder()
    embeddings = get_chunk_embeddings(chunks)
    add_chunks_to_chromadb(chunks, embeddings)
    collection = get_chromadb_collection()
    return collection, embedder, total_chunks
