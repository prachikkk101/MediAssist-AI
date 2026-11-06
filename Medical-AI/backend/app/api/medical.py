import logging
import os
import threading
import time
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.graph.workflow import workflow
from app.services.pdf_reader import extract_text_from_pdf
from app.services.ocr_reader import analyze_image

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/medical",
    tags=["Medical AI"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

UNREADABLE_MESSAGE = (
    "I couldn't read this document reliably. Please upload a clearer, upright "
    "photo or a typed PDF. Scanned PDFs should be uploaded as images."
)

NUTRITION_FALLBACK = (
    "This report doesn't contain findings that call for specific dietary changes. "
    "For general nutrition advice, please speak to your doctor or a dietitian."
)

# -------------------------
# In-memory job store (cleared when the server restarts)
# -------------------------
JOBS: dict = {}
JOBS_LOCK = threading.Lock()
RUN_LOCK = threading.Lock()  # one analysis at a time (single local Ollama/GPU)
JOB_TTL_SECONDS = 60 * 60


def _prune_jobs() -> None:
    cutoff = time.time() - JOB_TTL_SECONDS
    with JOBS_LOCK:
        for job_id in [j for j, v in JOBS.items() if v["created"] < cutoff]:
            del JOBS[job_id]


def _set_job(job_id: str, **fields) -> None:
    with JOBS_LOCK:
        JOBS[job_id].update(fields)


# -------------------------
# Shared helpers
# -------------------------
async def _save_upload(file: UploadFile):
    """Validate the file type, save it to disk, return (filename, extension, file_id, path)."""
    filename = file.filename or ""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF, JPG, JPEG or PNG.",
        )

    file_id = uuid.uuid4().hex
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{extension}")

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        logger.exception("Could not save upload")
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    return filename, extension, file_id, file_path


def _analyze(file_path: str, extension: str, file_id: str, filename: str, question: str) -> dict:
    """Blocking: extract text, run the agent workflow, build the response."""
    # -------------------------
    # Extract text + quality gate
    # -------------------------
    t0 = time.perf_counter()
    try:
        if extension == "pdf":
            text = (extract_text_from_pdf(file_path) or "").strip()
            readable = len(text) >= 50
            method = "pdf"
        else:
            ocr = analyze_image(file_path)
            text = ocr["text"]
            readable = ocr["readable"]
            method = ocr["method"]
    except Exception as e:
        logger.exception("Text extraction failed")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")

    logger.info(
        "Extraction done in %.1fs: file=%s method=%s chars=%d readable=%s",
        time.perf_counter() - t0, file_id, method, len(text), readable,
    )

    if not readable:
        raise HTTPException(status_code=422, detail=UNREADABLE_MESSAGE)

    # -------------------------
    # LangGraph state
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
        "route": "full_analysis",
    }

    # One thread per report so a new upload never inherits old history.
    config = {"configurable": {"thread_id": file_id}}

    # -------------------------
    # Run workflow
    # -------------------------
    t1 = time.perf_counter()
    try:
        result = workflow.invoke(state, config=config)
    except Exception as e:
        logger.exception("Workflow failed")
        raise HTTPException(
            status_code=500,
            detail=f"The analysis failed on the server: {e}",
        )
    logger.info("Workflow done in %.1fs", time.perf_counter() - t1)

    answer = (result.get("answer") or "").strip()
    explanation = (result.get("explanation") or answer).strip()
    summary = (result.get("summary") or "").strip()
    nutrition = (result.get("nutrition") or "").strip()

    if "UNREADABLE" in (answer.upper(), explanation.upper(), summary.upper()):
        raise HTTPException(status_code=422, detail=UNREADABLE_MESSAGE)

    if not nutrition:
        logger.warning("Nutrition agent returned empty output for %s", file_id)
        nutrition = NUTRITION_FALLBACK

    return {
        "report_id": file_id,
        "filename": filename,
        "extraction_method": method,
        "extracted_text": text[:500],
        "answer": answer,
        "summary": summary,
        "explanation": explanation,
        "nutrition": nutrition,
    }


def _run_job(job_id: str, file_path: str, extension: str, filename: str, question: str) -> None:
    """Runs in a background thread."""
    try:
        with RUN_LOCK:  # later jobs stay "queued" until this one finishes
            _set_job(job_id, status="running")
            result = _analyze(file_path, extension, job_id, filename, question)
        _set_job(job_id, status="done", result=result)
    except HTTPException as e:
        _set_job(job_id, status="error", http_status=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception("Job failed")
        _set_job(
            job_id,
            status="error",
            http_status=500,
            detail=f"The analysis failed on the server: {e}",
        )


# -------------------------
# Original endpoint (unchanged behaviour; Chat.tsx still uses it)
# -------------------------
@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    question: str = Form("Explain my report"),
):
    filename, extension, file_id, file_path = await _save_upload(file)
    return await run_in_threadpool(_analyze, file_path, extension, file_id, filename, question)


# -------------------------
# New: background job endpoints
# -------------------------
@router.post("/jobs", status_code=202)
async def create_job(
    file: UploadFile = File(...),
    question: str = Form("Explain my report"),
):
    filename, extension, job_id, file_path = await _save_upload(file)

    _prune_jobs()
    with JOBS_LOCK:
        JOBS[job_id] = {
            "status": "queued",
            "created": time.time(),
            "result": None,
            "detail": None,
            "http_status": None,
        }

    threading.Thread(
        target=_run_job,
        args=(job_id, file_path, extension, filename, question),
        daemon=True,
    ).start()

    return {"job_id": job_id, "status": "queued"}


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        snapshot = dict(job) if job else None

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found. It may have expired or the server was restarted.",
        )

    return {
        "job_id": job_id,
        "status": snapshot["status"],  # queued | running | done | error
        "result": snapshot["result"],
        "detail": snapshot["detail"],
        "http_status": snapshot["http_status"],
    }