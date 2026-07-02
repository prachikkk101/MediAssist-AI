import easyocr

# Load OCR model once
reader = easyocr.Reader(["en"])


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using EasyOCR.
    """

    result = reader.readtext(image_path)

    extracted_text = ""

    for detection in result:
        extracted_text += detection[1] + "\n"

    return extracted_text