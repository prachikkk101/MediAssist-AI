import easyocr

reader = easyocr.Reader(["en"])


def extract_text_from_image(image_path: str):
    result = reader.readtext(image_path)

    text = ""

    for item in result:
        text += item[1] + "\n"

    return text