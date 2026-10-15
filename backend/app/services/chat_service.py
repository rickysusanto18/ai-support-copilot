import logging

from sqlalchemy.orm import Session

from app.llm.ollama_client import ollama_client, LLMServiceError
from app.llm.prompt_builder import build_rag_prompt
from app.schemas.chat import ChatResponse, Citation
from app.services.retrieval_service import search_documents
from app.schemas.rag import RAGPipelineResult
from app.schemas.metrics import RAGMetrics
from app.core.config import settings

logger = logging.getLogger(__name__)

def run_rag_pipeline(
        db:Session,
        question: str,
        top_k: int = 5,
        min_similarity: float | None = None,
        request_id: str | None = None,
) -> RAGPipelineResult:
    effective_min_similarity = (
        settings.retrieval_min_similarity
        if min_similarity is None else min_similarity
    )
    
    search_response = search_documents(
        db=db,
        query=question,
        top_k=top_k,
        min_similarity=effective_min_similarity,
    )

    # No retrieved chunk
    if not search_response.results:
        metrics = RAGMetrics(
            retrieved_chunks=0,
            retrieval_confidence=0.0,
            cited_chunks=0,
            used_fallback=True,
            fallback_reason="no_relevant_context",
            llm_failed=False,
        )

        logger.info(
            "RAG fallback: request_id=%s reason=no_relevant_context",
            request_id,
        )

        return RAGPipelineResult(
            answer="Sorry, I don't have enough information to answer the question",
            retrieved_chunk_ids=[],
            cited_chunk_ids=[],
            citation_document_ids={},
            retrieval_confidence=0.0,
            used_fallback=True,
            llm_failed=False,
            metrics=metrics,
        )

    prompt = build_rag_prompt(
        question=question,
        results=search_response.results,
    )

    retrieval_confidence = max(
        result.similarity
        for result in search_response.results
    )

    retrieved_chunk_ids = [
        result.chunk_id
        for result in search_response.results
    ]

    citation_document_ids = {
        result.chunk_id: result.document_id
        for result in search_response.results
    }

    # Low retrieval confidence
    if retrieval_confidence < effective_min_similarity:
        metrics = RAGMetrics(
            retrieved_chunks=len(retrieved_chunk_ids),
            retrieval_confidence=retrieval_confidence,
            cited_chunks=0,
            used_fallback=True,
            fallback_reason="low_retrieval_confidence",
            llm_failed=False,
        )

        logger.info(
            "RAG fallback: request_id=%s reason=low_retrieval_confidence confidence=%.3f threshold=%.3f",
            request_id,
            retrieval_confidence,
            effective_min_similarity,
        )

        return RAGPipelineResult(
            answer=("I don't have enough information to answer that question"),
            retrieved_chunk_ids=retrieved_chunk_ids,
            cited_chunk_ids=[],
            citation_document_ids=citation_document_ids,
            retrieval_confidence=retrieval_confidence,
            used_fallback=True,
            llm_failed=False,
            metrics=metrics,
        )

    try:
        llm_answer = ollama_client.generate(prompt)
    except LLMServiceError:
        # LLM Failure
        metrics = RAGMetrics(
            retrieved_chunks=len(retrieved_chunk_ids),
            retrieval_confidence=retrieval_confidence,
            cited_chunks=0,
            used_fallback=True,
            fallback_reason="llm_failure",
            llm_failed=True,
        )

        logger.warning(
            "RAG fallback: request_id=%s reason=llm_failure retrieved_chunks=%d",
            request_id,
            len(retrieved_chunk_ids),
        )

        return RAGPipelineResult(
            answer=("Sorry, unable to generate answer now. Please try again later"),
            retrieved_chunk_ids=retrieved_chunk_ids,
            cited_chunk_ids=[],
            citation_document_ids=citation_document_ids,
            retrieval_confidence=retrieval_confidence,
            used_fallback=True,
            llm_failed=True,
            metrics=metrics,
        )

    # Successfully retrieved answer
    retrieved_chunk_id_set = set(retrieved_chunk_ids)

    validate_citation_chunk_ids = [
        chunk_id
        for chunk_id in llm_answer.citation_chunk_ids
        if chunk_id in retrieved_chunk_id_set
    ]

    metrics = RAGMetrics(
        retrieved_chunks=len(retrieved_chunk_ids),
        retrieval_confidence=retrieval_confidence,
        cited_chunks=len(validate_citation_chunk_ids),
        used_fallback=False,
        fallback_reason=None,
        llm_failed=False,
    )

    logger.info(
        "RAG success: request_id=%s retrieved_chunks=%d confidence=%.3f cited_chunks=%d",
        request_id,
        len(retrieved_chunk_ids),
        retrieval_confidence,
        len(llm_answer.citation_chunk_ids),
    )

    return RAGPipelineResult(
        answer=llm_answer.answer,
        retrieved_chunk_ids=retrieved_chunk_ids,
        cited_chunk_ids=validate_citation_chunk_ids,
        citation_document_ids=citation_document_ids,
        retrieval_confidence=retrieval_confidence,
        used_fallback=False,
        llm_failed=False,
        metrics=metrics,
    )

def generate_answer(
        db: Session,
        question: str,
        top_k: int = 5,
        min_similarity: float | None = None,
        request_id: str | None = None,
) -> ChatResponse:
    result = run_rag_pipeline(
        db=db,
        question=question,
        top_k=top_k,
        min_similarity=min_similarity,
        request_id=request_id
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