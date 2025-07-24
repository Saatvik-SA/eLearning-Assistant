# --- Utilities/PDF.py ---
import fitz  # PyMuPDF
from fpdf import FPDF
import os

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

def clean_text_for_pdf(text):
    """Clean text for PDF output, replacing problematic unicode chars with ASCII."""
    replacements = {
        '–': '-', '—': '-', '“': '"', '”': '"', '‘': "'", '’': "'", '…': '...', '°': ' degrees', '×': 'x', '÷': '/',
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return text.encode('latin-1', 'replace').decode('latin-1')


def export_text_to_pdf(text, filename, title=None, font_size=12, clean=True):
    """Generic utility to export text to a PDF file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=font_size)
    if title:
        pdf.set_font("Arial", 'B', font_size+2)
        pdf.cell(0, 10, txt=title, ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", size=font_size)
    for line in text.strip().split("\n"):
        if clean:
            line = clean_text_for_pdf(line)
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    return filename


def export_answer_key_to_pdf(answer_text, filename="Generated_Answer_Key.pdf"):
    """Export answer key text to PDF."""
    return export_text_to_pdf(answer_text, filename, title="Answer Key")


def export_feedback_to_pdf(feedback_text, filename="Data/Output/Student_Feedback_Report.pdf"):
    """Export feedback text to PDF."""
    return export_text_to_pdf(feedback_text, filename, title="Feedback Report")


def export_graded_report_to_pdf(graded_text, filename="Student_Graded_Report.pdf"):
    """Export graded report text to PDF."""
    return export_text_to_pdf(graded_text, filename, title="Graded Report")


def export_quiz_to_pdf(quiz_text, filename):
    """Export quiz text to PDF."""
    return export_text_to_pdf(quiz_text, filename, title="Quiz")


def export_revision_kit_to_pdf(text, filename="Data/Output/Revision_Kit.pdf"):
    """Export revision kit text to PDF."""
    return export_text_to_pdf(text, filename, title="Revision Kit")


def export_parent_report_to_pdf(report_text, filename, chart_path=None):
    """Export parent report text and optional chart image to PDF."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in report_text.strip().split("\n"):
        line = clean_text_for_pdf(line)
        pdf.multi_cell(0, 10, line)
    if chart_path and os.path.exists(chart_path):
        pdf.add_page()
        pdf.cell(0, 10, txt="Progress Chart", ln=True)
        pdf.image(chart_path, w=180)
    pdf.output(filename)
    return filename
