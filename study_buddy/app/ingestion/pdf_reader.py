from PyPDF2 import PdfReader
from io import BytesIO


def extract_text_from_pdf(file_bytes):
    pdf_stream = BytesIO(file_bytes)  # wrap bytes
    reader = PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# def extract_text_from_pdf(file_bytes):
#     reader = PdfReader(file_bytes)
#     return "\n".join([page.extract_text() for page in reader.pages])
