from pydantic import BaseModel, Field

from app.schemas.metrics import RAGMetrics

class RAGResult(BaseModel):
    answer: str
    obtained_chunk_id: list[int] = Field(default_factory=list)
    cited_chunk_id: list[int] = Field(default_factory=list)
    citation_document_id: dict[int, int] = Field(default_factory=dict)
    retrieval_confidence: float = 0.0
    is_using_fallback: bool = False
    is_llm_failed: bool = False
    metrics: RAGMetrics