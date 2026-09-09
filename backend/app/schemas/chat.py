from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        description="User's support question",
    )

class Citation(BaseModel):
    document_id: int
    chunk_id: int

class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    citations: list[Citation] = []
    tools_used: list[str] = []