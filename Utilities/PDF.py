# --- Utilities/PDF.py ---
import fitz  # PyMuPDF

def extract_text_from_pdf_path(pdf_path):
    """Extract full text from a single PDF file path as a single string."""
    with fitz.open(pdf_path) as doc:
        return "".join(page.get_text() for page in doc).strip()

def extract_texts_from_folder(folder_path):
    """Extracts text from all PDF files in a folder. Returns a list of strings."""
    import os
    texts = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.pdf'):
            with fitz.open(os.path.join(folder_path, file)) as doc:
                texts.append("".join(page.get_text() for page in doc).strip())
    return texts

def extract_texts_from_files(file_paths):
    """Extracts text from a list of PDF file paths. Returns a list of strings."""
    texts = []
    for path in file_paths:
        with fitz.open(path) as doc:
            texts.append("".join(page.get_text() for page in doc).strip())
    return texts
