from sqlalchemy.orm import Session

from app.llm.ollama_client import ollama_client, LLMServiceError
from app.llm.prompt_builder import build_rag_prompt
from app.schemas.chat import ChatResponse, Citation
from app.services.retrieval_service import search_documents

def generate_answer(
        db: Session,
        question: str,
        top_k: int = 5,
        min_similarity: float = 0.35,
) -> ChatResponse:
    search_response = search_documents(
        db=db,
        query=question,
        top_k=top_k,
        min_similarity=min_similarity,
    )

    # Reliability guard if chunk return 0
    if not search_response.results:
        return ChatResponse(
            answer="I'm sorry. I don't have enough information to answer that question.",
            confidence=0.0,
            citations=[],
            tools_used=[],
        )

    prompt = build_rag_prompt(
        question=question,
        results=search_response.results,
    )

    try:
        llm_answer = ollama_client.generate(prompt)

    except LLMServiceError:
        return ChatResponse(
            answer="Sorry, I'm unable to generate an answer right now. Please try again later",
            confidence=0.0,
            citations=[],
            tools_used=[],
        )

    citations = []

    for result in search_response.results:
        if result.chunk_id in llm_answer.citation_chunk_ids:
            citations.append(
                Citation(
                    document_id=result.document_id,
                    chunk_id=result.chunk_id,
                )
            )

    return ChatResponse(
        answer=llm_answer.answer,
        confidence=llm_answer.confidence,
        citations=citations,
        tools_used=[],
    )