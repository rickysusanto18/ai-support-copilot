from fastapi import FastAPI

from app.api.routes import router
from app.db.init_db import init_db

app = FastAPI(
    title="AI Support Copilot",
    description="This is just your another Multimodal RAG Example Application :)",
    version="0.1.0",
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(
    router,
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