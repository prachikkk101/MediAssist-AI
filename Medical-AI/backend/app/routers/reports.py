import os
import shutil
import json

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.report import Report

from ..utils.pdf_reader import extract_text_from_pdf
from ..utils.ocr import extract_text_from_image
from ..parser.parser import parse_medical_report


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# ==========================================
# Upload Folder
# ==========================================

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==========================================
# Allowed File Types
# ==========================================

ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/jpg"
}

# ==========================================
# Upload Report API
# ==========================================

@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # --------------------------------------
    # Validate File Type
    # --------------------------------------

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG, JPEG and PNG files are allowed."
        )

    # --------------------------------------
    # Save Uploaded File
    # --------------------------------------

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # --------------------------------------
    # Extract Text
    # --------------------------------------

    extracted_text = ""

    if file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(file_path)

    elif file.content_type in {
        "image/jpeg",
        "image/png",
        "image/jpg"
    }:
        extracted_text = extract_text_from_image(file_path)

    # --------------------------------------
    # Parse Medical Report
    # --------------------------------------

    parsed_report = parse_medical_report(extracted_text)

    # --------------------------------------
    # Save Metadata in Database
    # --------------------------------------

    report = Report(
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        extracted_text=extracted_text,
        parsed_json=json.dumps(parsed_report)
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    # --------------------------------------
    # API Response
    # --------------------------------------

    return {
        "success": True,
        "message": "File uploaded successfully.",

        "report": {
            "id": report.id,
            "filename": report.filename,
            "file_type": report.file_type,
            "file_path": report.file_path,
            "uploaded_at": report.uploaded_at
        },

        "raw_text": extracted_text,

        "parsed_report": parsed_report
    }
#ocr = optical character recognization as pypdf can only extract data from pdf
# but it can not read digital pdf therefore we will use ocr
# suppose what if patient does not upload pdf but uploaded image or digital pdf

              #User
               # │
               # ▼
         #Upload File
               # │
        #┌───────┴────────┐
        #│                │
        #▼                #▼
      #PDF             Image
       # │                │
        #▼                ▼
     #PyPDF          EasyOCR
       # │                │
       # └───────┬────────┘
        #        ▼
        #Extracted Text
         #       │
          #      ▼
          #Parser Agent


       #Image

        #↓

    #Detect Characters

        #↓

    #Detect Words

        #↓

    #Combine Words

        #↓

    #Return Text