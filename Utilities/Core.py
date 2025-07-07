# --- Utilities/Core.py ---

import os
from tkinter import filedialog, Tk
import fitz
from Utilities.Embeddings import get_embedder
from Utilities.ChromaDB import add_chunks_to_chromadb, get_chromadb_collection

# === PDF Upload Dialogs ===

def upload_study_pdfs():
    """
    Upload academic content PDFs into Data/Upload.
    """
    return _upload_pdfs_to_folder("Data/Upload")


def upload_answer_pdfs():
    """
    Upload student answer sheets into Data/Answers.
    """
    return _upload_pdfs_to_folder("Data/Answers")


def _upload_pdfs_to_folder(target_folder):
    """
    Generic function to upload PDFs to a given folder.
    """
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

# === File Selection ===

def select_pdf_file(title="Select PDF file"):
    """
    Show file dialog and return selected PDF path.
    """
    root = Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_path = filedialog.askopenfilename(title=title, filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    return file_path


# === PDF Loading & Embedding ===

def load_and_chunk_pdfs(folder="Data/Upload"):
    """
    Extracts text from all PDFs in a given folder.
    """
    all_texts = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            with fitz.open(os.path.join(folder, file)) as doc:
                text = "".join([page.get_text() for page in doc])
                all_texts.append(text)
    return all_texts


def embed_and_store_chunks(chunks):
    """
    Embeds and stores chunks in ChromaDB.
    """
    embedder = get_embedder()
    embeddings = embedder.encode(chunks, show_progress_bar=True)
    add_chunks_to_chromadb(chunks, embeddings)
    return get_chromadb_collection(), embedder


# === Full Pipeline for Study Material ===

def prepare_academic_context():
    """
    Loads and embeds study PDFs from Data/Upload.
    Returns: (collection, embedder, total_chunks)
    """
    chunks = load_and_chunk_pdfs("Data/Upload")
    total_chunks = len(chunks)
    collection, embedder = embed_and_store_chunks(chunks)
    return collection, embedder, total_chunks
