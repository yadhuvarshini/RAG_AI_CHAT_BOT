from PyPDF2 import PdfReader
from docx import Document

def extract_text(file_path):
    """
    Extracts text from a PDF or DOCX file.
    
    Args:
        file_path (str): The path to the file.
        
    Returns:
        str: The extracted text.
    """
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
        return text.strip()
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text.strip()
    elif file_path.endswith('.txt'):
        with open(file_path,r,encoding='utf-8') as file:
            return file.read().strip()
    else:
        raise ValueError("Unsupported file format. Only PDF, DOCX, and TXT files are supported.")