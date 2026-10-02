from sqlalchemy.orm import Session

from app.llm.ollama_client import ollama_client, LLMServiceError
from app.llm.prompt_builder import build_rag_prompt
from app.schemas.chat import ChatResponse, Citation
from app.services.retrieval_service import search_documents
from app.schemas.rag import RAGPipelineResult

def run_rag_pipeline(
        db:Session,
        question: str,
        top_k: int = 5,
        min_similarity: float = 0.35,
) -> RAGPipelineResult:
    search_response = search_documents(
        db=db,
        query=question,
        top_k=top_k,
        min_similarity=min_similarity,
    )

    if not search_response.results:
        return RAGPipelineResult(
            answer="Sorry, I don't have enough information to answer the question",
            retrieved_chunk_ids=[],
            cited_chunk_ids=[],
            citation_document_ids={},
            retrieval_confidence=0.0,
            used_fallback=True,
            llm_failed=False,
        )

    prompt = build_rag_prompt(
        question=question,
        results=search_response.results,
    )

    retrieval_confidence = max(
        result.similarity
        for result in search_response
    )

    retrieved_chunk_ids = [
        result.chunk_id
        for result in search_response.results
    ]

    citation_document_ids = {
        result.chunk_id: result.document_id
        for result in search_response.results
    }

    try:
        llm_answer = ollama_client.generate(prompt)
    except LLMServiceError:
        return RAGPipelineResult(
            answer=(
                "Sorry, unable to generate answer now. Please try again later"
            ),
            retrieved_chunk_ids=retrieved_chunk_ids,
            cited_chunk_ids=[],
            citation_document_ids=citation_document_ids,
            retrieval_confidence=retrieval_confidence,
            used_fallback=True,
            llm_failed=True,
        )

    return RAGPipelineResult(
        answer=llm_answer.answer,
        retrieved_chunk_ids=retrieved_chunk_ids,
        cited_chunk_ids=llm_answer.citation_chunk_ids,
        citation_document_ids=citation_document_ids,
        retrieval_confidence=retrieval_confidence,
        used_fallback=False,
        llm_failed=False,
    )

def generate_answer(
        db: Session,
        question: str,
        top_k: int = 5,
        min_similarity: float = 0.35,
) -> ChatResponse:
    result = run_rag_pipeline(
        db=db,
        question=question,
        top_k=top_k,
        min_similarity=min_similarity,
    )

    citations = [
        Citation(
            document_id=result.citation_document_ids[chunk_id],
            chunk_id=chunk_id,
        )
        for chunk_id in result.cited_chunk_ids
        if chunk_id in result.citation_document_ids
    ]


    return ChatResponse(
        answer=result.answer,
        confidence=(
            result.retrieval_confidence
            if not result.llm_failed
            else 0.0
        ),
        citations=citations,
        tools_used=[],
    )