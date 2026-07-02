from app.services.ocr_reader import extract_text_from_image
from pdf2image import convert_from_path
import os
import tempfile


def ocr_agent(state):
    """
    Extract text from scanned PDFs using OCR.
    """

    pdf_path = state["file_path"]

    pages = convert_from_path(pdf_path)

    extracted_text = ""

    with tempfile.TemporaryDirectory() as temp_dir:

        for i, page in enumerate(pages):

            image_path = os.path.join(temp_dir, f"page_{i}.png")

            page.save(image_path, "PNG")

            extracted_text += extract_text_from_image(image_path)
            extracted_text += "\n"

    state["report_text"] = extracted_text

    return state