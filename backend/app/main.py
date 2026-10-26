import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from time import perf_counter

from app.api.routes import router as api_router
from app.db.init_db import init_db

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
)

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        start_time = perf_counter()

        logger = logging.getLogger("app.requests")

        logger.info(
            "Request started: id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Request failed: id=%s method=%s path=%s",
                request_id,
                request.method,
                request.url.path,
            )

            raise

        response.headers["X-Request-ID"] = request_id

        duration_ms = (perf_counter() - start_time) * 1000

        logger.info(
            "Request compeleted: id=%s status=%d duration_ms=%.2f",
            request_id,
            response.status_code,
            duration_ms,
        )

        return response

app = FastAPI(
    title="AI Support Copilot",
    description="This is just your another Multimodal RAG Example Application :)",
    version="0.1.0",
)

app.add_middleware(
    RequestIDMiddleware,
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Request-ID"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(
    api_router,
    prefix="/api/v1",
)

@app.get("/")
def root():
    return {
        "message": "AI Support Copilot API",
        "version": "0.1.0",
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

# run uvicorn app.main:app --reload
# Open:                 http://127.0.0.1:8000
# API Documentation:    http://127.0.0.1:8000/docs