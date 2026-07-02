from pypdf import PdfReader
import fitz
import os

from app.utils.ocr import extract_text_from_image



def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF.
    Uses normal PDF extraction first.
    If empty, uses OCR.
    """


    # -------------------------
    # 1. Try normal PDF reading
    # -------------------------

    reader = PdfReader(pdf_path)

    extracted_text = ""


    for page in reader.pages:

        text = page.extract_text()


        if text:

            extracted_text += text + "\n"



    # If text exists return it
    if extracted_text.strip():

        return extracted_text



    # -------------------------
    # 2. OCR fallback
    # -------------------------

    print(
        "No text found. Running OCR..."
    )


    doc = fitz.open(pdf_path)


    ocr_text = ""


    for index, page in enumerate(doc):


        pix = page.get_pixmap()


        image_path = (
            f"temp_page_{index}.png"
        )


        pix.save(image_path)



        ocr_text += extract_text_from_image(
            image_path
        )


        os.remove(image_path)



    return ocr_text