# --- Utilities/PDF.py ---
import fitz  # PyMuPDF

def extract_text_from_pdf_path(pdf_path):
    """Extract full text from a single PDF path."""
    with fitz.open(pdf_path) as doc:
        return "".join(page.get_text() for page in doc).strip()

def extract_text_from_uploaded_files(uploaded_files):
    """Extract text from uploaded files dictionary."""
    full_texts = []
    for filename in uploaded_files.keys():
        with fitz.open(filename) as doc:
            text = "".join(page.get_text() for page in doc)
        full_texts.append(text)
    return full_texts
