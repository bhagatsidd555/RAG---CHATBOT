"""
pdf_extractor.py

Extract text from PDFs:
- Native extraction (PyMuPDF)
- OCR fallback for scanned PDFs
- Auto detect mixed PDFs
- Better OCR preprocessing
"""

import os
import sys
import fitz
import pytesseract
from PIL import Image
import io
from typing import List, Dict

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

from config import OCR_LANG, OCR_DPI


MIN_TEXT_LENGTH = 50


def is_page_scanned(
    page: fitz.Page,
    min_text_len: int = MIN_TEXT_LENGTH
) -> bool:

    try:

        text = page.get_text(
            "text"
        ).strip()

        return len(text) < min_text_len

    except:

        return True


def preprocess_image(img):

    img = img.convert(
        "L"
    )

    return img


def ocr_page(
    page: fitz.Page
):

    try:

        zoom = OCR_DPI / 72

        mat = fitz.Matrix(
            zoom,
            zoom
        )

        pix = page.get_pixmap(
            matrix=mat,
            colorspace=fitz.csRGB
        )

        img = Image.open(
            io.BytesIO(
                pix.tobytes("png")
            )
        )

        img = preprocess_image(
            img
        )

        text = pytesseract.image_to_string(

            img,

            lang=OCR_LANG,

            config="--psm 6"
        )

        return text

    except Exception as e:

        print(
f"[OCR Error page {page.number+1}] {e}"
        )

        return ""


def extract_pdf(
    pdf_path: str
) -> List[Dict]:

    filename = os.path.basename(
        pdf_path
    )

    pages = []

    try:

        doc = fitz.open(
            pdf_path
        )

    except Exception as e:

        print(
f"[ERROR opening PDF]{e}"
        )

        return []


    print(
f"\nProcessing {filename}"
    )

    print(
f"Pages:{len(doc)}"
    )


    native_count = 0
    ocr_count = 0


    for page_num in range(
        len(doc)
    ):

        page = doc[
            page_num
        ]

        use_ocr = is_page_scanned(
            page
        )


        if use_ocr:

            text = ocr_page(
                page
            )

            source_type = "ocr"

            ocr_count += 1

        else:

            text = page.get_text(
                "text"
            )

            source_type = "native"

            native_count += 1


        text = text.strip()

        if len(text) > 5:

            pages.append({

                "page_num":
                page_num + 1,

                "text":
                text,

                "source_type":
                source_type,

                "filename":
                filename,

                "pdf_path":
                pdf_path

            })


    doc.close()

    print(
f"Native pages:{native_count}"
    )

    print(
f"OCR pages:{ocr_count}"
    )

    print(
f"Extracted:{len(pages)}"
    )

    return pages