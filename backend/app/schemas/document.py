from pydantic import BaseModel, Field

class DocumentCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    content: str = Field(
        min_length=1,
    )

    source: str | None = Field(
        default=None,
        max_length=500,
    )

class DocumentResponse(BaseModel):
    id: int
    title: str
    source: str | None