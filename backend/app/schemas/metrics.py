from typing import Literal

from pydantic import BaseModel, Field, model_validator

FallbackReason = Literal[
    "no_relevant_context",
    "low_retrieval_confidence",
    "llm_failure",
]

class RAGMetrics(BaseModel):
    retrieved_chunks: int = Field(ge=0)
    retrieval_confidence: float = Field(ge=0.0, le=1.0)
    cited_chunks: int = Field(ge=0)
    used_fallback: bool
    fallback_reason: FallbackReason | None
    llm_failed:bool

    #  Pydantic v2 validator that runs after all fields are parsed
    @model_validator(mode="after")
    def validate_fallback_state(self):
        if self.used_fallback and self.fallback_reason is None:
            raise ValueError(
                "A fallback must have a fallback reason."
            )

        if not self.used_fallback and self.fallback_reason is not None:
            raise ValueError(
                "A successful response cannot have a fallback reason."
            )

        if self.llm_failed and self.fallback_reason != "llm_failure":
            raise ValueError(
                "An LLM failure must use the llm_failure reason."
            )

        if self.fallback_reason == "llm_failure" and not self.llm_failed:
            raise ValueError(
                "The llm_failure reason requires llm_failed=True."
            )

        return self