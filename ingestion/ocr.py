import pytesseract
from pdf2image import convert_from_path

def extract_text_ocr(pdf_path):

    pages = convert_from_path(pdf_path)

    full_text=[]

    for i,page in enumerate(pages):

        text = pytesseract.image_to_string(page)

        full_text.append(text)

    return "\n".join(full_text)