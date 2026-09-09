from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="The user's message",
    )

class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    citations: list[str] = []
    tools_used: list[str] = []