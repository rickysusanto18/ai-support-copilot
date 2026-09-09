from sqlalchemy.orm import Session

from app.llm.ollama_client import ollama_client
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

    prompt = build_rag_prompt(
        question=question,
        results=search_response.results,
    )

    llm_answer = ollama_client.generate(prompt)

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