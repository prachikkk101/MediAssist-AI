import io
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageOps
from pytesseract import Output


def _score(img: Image.Image) -> int:
    """Count confidently-read real words; used to pick the right rotation."""
    small = img.copy()
    small.thumbnail((1200, 1200))
    d = pytesseract.image_to_data(small, config="--psm 6", output_type=Output.DICT)
    return sum(
        1
        for t, c in zip(d["text"], d["conf"])
        if len(t.strip()) >= 3 and t.strip().isalpha() and float(c) > 60
    )


def _auto_rotate(img: Image.Image) -> Image.Image:
    candidates = [img.rotate(a, expand=True) for a in (0, 90, 180, 270)]
    return max(candidates, key=_score)


def _preprocess(img: Image.Image) -> Image.Image:
    g = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    if max(g.shape) < 2000:
        s = 2000 / max(g.shape)
        g = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    g = cv2.fastNlMeansDenoising(g, None, 15)
    g = cv2.adaptiveThreshold(
        g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    return Image.fromarray(g)


def extract_text(image_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img).convert("RGB")  # honour phone rotation
    img = _auto_rotate(img)
    clean = _preprocess(img)

    text = pytesseract.image_to_string(clean, config="--oem 3 --psm 6").strip()
    d = pytesseract.image_to_data(clean, config="--psm 6", output_type=Output.DICT)
    words = [
        t for t, c in zip(d["text"], d["conf"])
        if t.strip() and float(c) > 0
    ]
    good = [
        t for t, c in zip(d["text"], d["conf"])
        if len(t.strip()) >= 3 and t.strip().isalpha() and float(c) > 60
    ]
    ratio = len(good) / max(len(words), 1)

    return {
        "text": text,
        "readable": len(good) >= 15 and ratio >= 0.4,
        "good_words": len(good),
        "ratio": round(ratio, 2),
    }