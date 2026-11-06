import io
import logging
import os
import shutil

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageOps
from pytesseract import Output

logger = logging.getLogger(__name__)

# "vlm" = local vision model via Ollama (falls back to Tesseract if unavailable)
# "tesseract" = Tesseract only
OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").lower()
VLM_MODEL = os.getenv("OCR_VLM_MODEL", "qwen2.5vl:7b")
VLM_MAX_SIDE = 1800

VLM_PROMPT = (
    "Transcribe all the text in this medical document exactly as written. "
    "Keep every label together with its value on one line, for example "
    "'Patient Name: ...' and 'Age/Gender: ...'. Include header tables, names, "
    "IDs, dates and hospital or lab names. Do not summarize, explain or add "
    "anything. Write [illegible] for anything you cannot read. Output plain text only."
)

# -------------------------------------------------------------------
# Locate tesseract.exe (PATH first, then default Windows install paths)
# -------------------------------------------------------------------
_TESSERACT_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def _configure_tesseract():
    found = shutil.which("tesseract")
    if found:
        pytesseract.pytesseract.tesseract_cmd = found
        return
    for path in _TESSERACT_CANDIDATES:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return
    logger.error("Tesseract not found. Install it or set tesseract_cmd manually.")


_configure_tesseract()


# -------------------------------------------------------------------
# Tesseract helpers
# -------------------------------------------------------------------
def _good_words(d: dict) -> list:
    """Words that look like real, confidently-read words."""
    return [
        t for t, c in zip(d["text"], d["conf"])
        if len(t.strip()) >= 3 and t.strip().isalpha() and float(c) > 60
    ]


def _score(img: Image.Image) -> int:
    small = img.copy()
    small.thumbnail((1500, 1500))
    d = pytesseract.image_to_data(small, config="--psm 6", output_type=Output.DICT)
    return len(_good_words(d))


def _auto_rotate(img: Image.Image) -> Image.Image:
    """Try 0/90/180/270 degrees and keep the orientation that reads best."""
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


def _preprocess_gray(img: Image.Image) -> Image.Image:
    g = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    if max(g.shape) < 2400:
        s = 2400 / max(g.shape)
        g = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return Image.fromarray(clahe.apply(g))


def _best_ocr(variants):
    """Try each preprocessing variant and layout mode; keep the one reading most words."""
    best = None
    for im in variants:
        for psm in (6, 4):
            cfg = f"--oem 3 --psm {psm}"
            d = pytesseract.image_to_data(im, config=cfg, output_type=Output.DICT)
            good = _good_words(d)
            if best is None or len(good) > len(best["good"]):
                best = {"img": im, "cfg": cfg, "d": d, "good": good}
    return best


# -------------------------------------------------------------------
# Local vision model (Ollama)
# -------------------------------------------------------------------
def _read_with_vlm(img: Image.Image) -> str:
    try:
        import ollama

        im = img.copy()
        im.thumbnail((VLM_MAX_SIDE, VLM_MAX_SIDE))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=92)

        client = ollama.Client(timeout=300)
        resp = client.chat(
            model=VLM_MODEL,
            messages=[{
                "role": "user",
                "content": VLM_PROMPT,
                "images": [buf.getvalue()],
            }],
            options={"temperature": 0},
        )
        return (resp["message"]["content"] or "").strip()
    except Exception as e:
        logger.warning(
            "Vision OCR unavailable (%s). Pull the model with: ollama pull %s",
            e, VLM_MODEL,
        )
        return ""


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------
def analyze_image(path: str) -> dict:
    """Returns {text, readable, method, good_words, ratio}."""
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    img = _auto_rotate(img)

    if OCR_ENGINE == "vlm":
        vlm_text = _read_with_vlm(img)
        if len(vlm_text) >= 40:
            logger.info("Vision OCR used (%d chars)", len(vlm_text))
            return {"text": vlm_text, "readable": True, "method": "vlm",
                    "good_words": 0, "ratio": 0.0}
        logger.warning("Vision OCR gave no usable text; falling back to Tesseract")

    best = _best_ocr([_preprocess(img), _preprocess_gray(img)])
    text = pytesseract.image_to_string(best["img"], config=best["cfg"]).strip()
    d = best["d"]
    all_words = [t for t, c in zip(d["text"], d["conf"]) if t.strip() and float(c) > 0]
    good = _good_words(d)
    ratio = len(good) / max(len(all_words), 1)
    readable = len(good) >= 15 and ratio >= 0.4

    logger.info(
        "Tesseract result: good_words=%d ratio=%.2f readable=%s",
        len(good), ratio, readable,
    )

    return {"text": text, "readable": readable, "method": "ocr",
            "good_words": len(good), "ratio": round(ratio, 2)}


def extract_text_from_image(path: str) -> str:
    """Backward-compatible wrapper for any other code still calling this."""
    return analyze_image(path)["text"]