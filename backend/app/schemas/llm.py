from pydantic import BaseModel, Field

class LLMAnswer(BaseModel):
    answer: str = Field(
        min_length=1,
    )

    citation_chunk_ids: list[int]