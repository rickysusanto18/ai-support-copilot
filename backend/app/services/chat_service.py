import logging

from sqlalchemy.orm import Session

from app.llm.ollama_client import ollama_client, LLMServiceError
from app.llm.prompt_builder import build_rag_prompt
from app.schemas.chat import ChatResponse, Citation
from app.services.retrieval_service import search_documents
from app.schemas.rag import RAGResult
from app.schemas.metrics import RAGMetrics
from app.core.config import settings

logger = logging.getLogger(__name__)

def run_rag_pipeline(
        db:Session,
        question: str,
        top_k: int = 5,
        min_similarity: float | None = None,
        request_id: str | None = None,
) -> RAGResult:
    min_sim = min_similarity if min_similarity is not None else settings.retrieval_min_similarity
    
    search_response = search_documents(
        db=db,
        query=question,
        top_k=top_k,
        min_similarity=min_sim,
    )

    # Case 1: No retrieved chunk
    if not search_response.results:
        metrics = RAGMetrics(
            retrieved_chunk=0,
            retrieval_confidence=0.0,
            cited_chunk=0,
            is_used_fallback=True,
            fallback_reason="no_relevant_context",
            is_llm_failed=False,
        )

        logger.info("RAG fallback: request_id=%s reason=no_relevant_context", request_id)

        return RAGResult(
            answer="I don't have enough information to answer the question",
            is_using_fallback=True,
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

    retrieved_chunk_id = [
        result.chunk_id
        for result in search_response.results
    ]

    citation_document_id = {
        result.chunk_id: result.document_id
        for result in search_response.results
    }

    # Case 2: Low retrieval confidence
    if retrieval_confidence < min_sim:
        metrics = RAGMetrics(
            retrieved_chunk=len(retrieved_chunk_id),
            retrieval_confidence=retrieval_confidence,
            cited_chunk=0,
            is_used_fallback=True,
            fallback_reason="low_retrieval_confidence",
            is_llm_failed=False,
        )

        logger.info(
            "RAG fallback: request_id=%s reason=low_retrieval_confidence confidence=%.3f threshold=%.3f",
            request_id,
            retrieval_confidence,
            min_sim,
        )

        return RAGResult(
            answer=("I don't have enough information to answer that question"),
            obtained_chunk_id=retrieved_chunk_id,
            citation_document_id=citation_document_id,
            obtain_confidence=retrieval_confidence,
            is_using_fallback=True,
            metrics=metrics,
        )

    try:
        llm_answer = ollama_client.generate(prompt)
    except LLMServiceError:
        # Case 3: LLM Failure
        metrics = RAGMetrics(
            retrieved_chunk=len(retrieved_chunk_id),
            retrieval_confidence=retrieval_confidence,
            cited_chunk=0,
            is_used_fallback=True,
            fallback_reason="llm_failure",
            is_llm_failed=True,
        )

        logger.warning(
            "RAG fallback: request_id=%s reason=llm_failure retrieved_chunk=%d",
            request_id,
            len(retrieved_chunk_id),
        )

        return RAGResult(
            answer=("Unable to generate answer now. Please try again later"),
            obtained_chunk_id=retrieved_chunk_id,
            citation_document_id=citation_document_id,
            obtain_confidence=retrieval_confidence,
            is_using_fallback=True,
            is_llm_failed=True,
            metrics=metrics,
        )

    # Case 4: Successfully retrieved answer
    retrieved_chunk_id_set = set(retrieved_chunk_id)

    validate_citation_chunk_id = [
        chunk_id
        for chunk_id in llm_answer.citation_chunk_id
        if chunk_id in retrieved_chunk_id_set
    ]

    metrics = RAGMetrics(
        retrieved_chunk=len(retrieved_chunk_id),
        retrieval_confidence=retrieval_confidence,
        cited_chunk=len(validate_citation_chunk_id),
        is_used_fallback=False,
        fallback_reason=None,
        is_llm_failed=False,
    )

    logger.info(
        "RAG success: request_id=%s retrieved_chunk=%d confidence=%.3f cited_chunk=%d",
        request_id,
        len(retrieved_chunk_id),
        retrieval_confidence,
        len(llm_answer.citation_chunk_id),
    )

    return RAGResult(
        answer=llm_answer.answer,
        obtained_chunk_id=retrieved_chunk_id,
        cited_chunk_id=validate_citation_chunk_id,
        citation_document_id=citation_document_id,
        obtain_confidence=retrieval_confidence,
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
            document_id=result.citation_document_id[chunk_id],
            chunk_id=chunk_id,
        )
        for chunk_id in result.cited_chunk_id
        if chunk_id in result.citation_document_id
    ]


    return ChatResponse(
        answer=result.answer,
        confidence=(
            result.retrieval_confidence
            if not result.is_llm_failed
            else 0.0
        ),
        citations=citations,
        tools_used=[],
    )