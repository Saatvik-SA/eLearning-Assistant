# --- Utilities/PDF.py ---

import fitz  # PyMuPDF

def extract_text_from_pdf_path(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_uploaded_files(uploaded_files):
    full_texts = []
    for filename in uploaded_files.keys():
        with fitz.open(filename) as doc:
            pdf_text = ""
            for page in doc:
                pdf_text += page.get_text()
        full_texts.append(pdf_text)
    return full_texts