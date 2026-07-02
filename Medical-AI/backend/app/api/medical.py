from fastapi import APIRouter, UploadFile, File, Form, HTTPException

import os
import uuid

from app.graph.workflow import workflow
from app.services.pdf_reader import extract_text_from_pdf
from app.services.ocr_reader import extract_text_from_image


router = APIRouter(
    prefix="/medical",
    tags=["Medical AI"]
)

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@router.post("/upload")
async def upload_report(

    file: UploadFile = File(...),

    question: str = Form("Explain my report")

):

    # -------------------------
    # Save uploaded file
    # -------------------------

    extension = file.filename.lower().split(".")[-1]

    file_id = str(uuid.uuid4())

    file_path = f"{UPLOAD_DIR}/{file_id}.{extension}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # -------------------------
    # Extract Text
    # -------------------------

    if extension == "pdf":

        text = extract_text_from_pdf(file_path)

    elif extension in ["jpg", "jpeg", "png"]:

        text = extract_text_from_image(file_path)

    else:

        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF, JPG, JPEG or PNG."
        )

    print("\n========== EXTRACTED TEXT ==========")
    print(text)
    print("====================================")

    # -------------------------
    # LangGraph State
    # -------------------------

    state = {

        "report_text": text,

        "parsed_report": {},

        "question": question,

        "context": "",

        "answer": "",

        "summary": "",

        "explanation": "",

        "nutrition": "",

        "history": "",

        "route": ""

    }

    config = {

        "configurable": {

            "thread_id": "user_1"

        }

    }

    # -------------------------
    # Run Workflow
    # -------------------------

    result = workflow.invoke(
        state,
        config=config
    )

    print("\n========== FINAL STATE ==========")
    print(result)
    print("=================================")

    # -------------------------
    # Response
    # -------------------------

    return {

        "filename": file.filename,

        "extracted_text": text[:500],

        "answer": result.get("answer", ""),

        "summary": result.get("summary", ""),

        "explanation": result.get("explanation", ""),

        "nutrition": result.get("nutrition", "")

    }