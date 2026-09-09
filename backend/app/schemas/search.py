from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural language search query",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="No of chunks to retrieve",
    )

    min_similarity: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Minimum semantic similarity",
    )

class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    similarity: float

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]