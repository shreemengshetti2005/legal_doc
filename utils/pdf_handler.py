import pdfplumber
import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path, method="pdfplumber"):
    """
    Extracts text from PDF using the specified method.
    """
    text = ""

    if method == "pdfplumber":
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif method == "PyMuPDF":
        with fitz.open(pdf_path) as pdf:
            for page_num in range(len(pdf)):
                page = pdf.load_page(page_num)
                text += page.get_text()

    return text

def save_text_to_file(text, output_path):
    """Saves the extracted text to a text file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

# Example usage:
if __name__ == "__main__":
    pdf_path = "../data/sample1.pdf"
    output_path = "../export/sample1.txt"
    
    extracted_text = extract_text_from_pdf(pdf_path, method="pdfplumber")
    save_text_to_file(extracted_text, output_path)
    print(f"Text extracted and saved to {output_path}")
