from pydantic import BaseModel, Field

class LLMAnswer(BaseModel):
    answer: str = Field(
        min_length=1,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    citation_chunk_ids: list[int]