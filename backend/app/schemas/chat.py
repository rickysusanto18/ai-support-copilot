from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="User's support question",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty")

        return value

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