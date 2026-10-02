from pydantic import BaseModel

class RAGPipelineResult(BaseModel):
    answer: str
    retrieved_chunk_ids: list[int]
    cited_chunk_ids: list[int]
    citation_document_ids: dict[int, int]
    retrieval_confidence: float
    used_fallback: bool
    llm_failed: bool