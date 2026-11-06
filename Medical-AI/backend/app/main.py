import os
import sys
import logging

# Show our own INFO logs, but keep third-party libraries quiet
logging.basicConfig(level=logging.INFO)

for noisy in ("httpx", "httpcore", "huggingface_hub", "sentence_transformers", "urllib3"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.medical import router

app = FastAPI(
    title="Medical AI",
    version="1.0",
)

# Allowed browser origins:
#  - Vite dev server on any localhost / 127.0.0.1 port
#  - Your Vercel deployments (production and preview URLs)
# Optionally add one exact origin via the FRONTEND_ORIGIN env var.
ALLOWED_ORIGIN_REGEX = (
    r"http://(localhost|127\.0\.0\.1):\d+"
    r"|https://[a-zA-Z0-9-]+\.vercel\.app"
)
extra_origin = os.getenv("FRONTEND_ORIGIN")  # e.g. https://my-custom-domain.com

app.add_middleware(
    CORSMiddleware,
    allow_origins=[extra_origin] if extra_origin else [],
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def home():
    return {"success": True, "message": "Medical AI API running"}


@app.get("/health")
def health_check():
    return {"success": True, "status": "healthy"}