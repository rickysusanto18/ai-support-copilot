from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.document import DocumentCreate, DocumentResponse
from app.schemas.search import SearchRequest, SearchResponse
from app.services.document_service import create_document
from app.services.retrieval_service import search_documents
from app.services.chat_service import generate_answer

router = APIRouter()

@router.post("/chat", response_model = ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
    ):

    answer = generate_answer(
        db=db,
        question=request.message,
    )

    return ChatResponse(
        answer=answer,
        confidence=0.5,
        citations=[],
        tools_used=[],
    )

@router.post("/documents", response_model=DocumentResponse)
def create_document_endpoint(
    request: DocumentCreate,
    db: Session = Depends(get_db),
):
    doc = create_document(
        db=db,
        title=request.title,
        content=request.content,
        source=request.source,
    )

    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        source=doc.source
    )

@router.post("/search", response_model=SearchResponse)
def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    return search_documents(
        db=db,
        query=request.query,
        top_k=request.top_k,
        min_similarity=request.min_similarity,
    )