import sys
import pytest

from pathlib import Path
from pydantic import ValidationError
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

EVALUATION_PATH = Path(__file__).parent
BACKEND_PATH = Path(__file__).parents[2] / "backend"

sys.path.insert(0, str(EVALUATION_PATH))
sys.path.insert(0, str(BACKEND_PATH))

from run_evaluation import (evaluate_citations, evaluate_expected_behavior)
from app.schemas.metrics import RAGMetrics
from app.services.chat_service import run_rag_pipeline
from app.llm.ollama_client import LLMServiceError

def test_knowledge_base_behavior_passes_with_strong_retrieval():
    test_case = {
        "expected_behavior": "answer_from_knowledge_base",
        "expected_retrieval": "strong",
    }

    result = evaluate_expected_behavior(
        test_case=test_case,
        actual_has_results=True,
        top_similarity=0.75,
    )

    assert result is True

def test_knowledge_base_behavour_fails_with_weak_retrieval():
    test_case = {
        "expected_behavior": "answer_from_knowledge_base",
        "expected_retrieval": "strong",
    }

    result = evaluate_expected_behavior(
        test_case=test_case,
        actual_has_results=True,
        top_similarity=0.20,
    )

    assert result is False

def test_fallback_behavior_passes_without_results():
    test_case = {
        "expected_behavior": "fallback",
        "expected_retrieval": "none",
    }

    result = evaluate_expected_behavior(
        test_case=test_case,
        actual_has_results=False,
        top_similarity=0.0,
    )

    assert result is True

def test_fallback_behavior_fails_when_results_exist():
    test_case = {
        "expected_behavior": "fallback",
        "expected_retrieval": "none",
    }

    result = evaluate_expected_behavior(
        test_case=test_case,
        actual_has_results=True,
        top_similarity=0.80,
    )

    assert result is False

def test_citation_is_valid_when_chunk_was_retrieved():
    result = evaluate_citations(
        retrieved_chunk_ids=[1, 2, 3],
        cited_chunk_ids=[1, 3],
    )

    assert result is True

def test_citation_is_invalid_when_chunk_was_not_retrieved():
    result = evaluate_citations(
        retrieved_chunk_ids=[1, 2, 3],
        cited_chunk_ids=[99]
    )

    assert result is False

def test_no_context_records_correct_fallback_reason():
    metrics = RAGMetrics(
        retrieved_chunks=0,
        retrieval_confidence=0.0,
        cited_chunks=0,
        used_fallback=True,
        fallback_reason="no_relevant_context",
        llm_failed=False,
    )

    assert metrics.used_fallback is True
    assert metrics.fallback_reason == "no_relevant_context"
    assert metrics.llm_failed is False

def test_low_confidence_records_correct_fallback_reason():
    metrics = RAGMetrics(
        retrieved_chunks=1,
        retrieval_confidence=0.411,
        cited_chunks=0,
        used_fallback=True,
        fallback_reason="low_retrieval_confidence",
        llm_failed=False,
    )

    assert metrics.used_fallback is True
    assert metrics.fallback_reason == "low_retrieval_confidence"
    assert metrics.cited_chunks == 0

def test_llm_failure_records_correct_fallback_reason():
    metrics = RAGMetrics(
        retrieved_chunks=1,
        retrieval_confidence=0.648,
        cited_chunks=0,
        used_fallback=True,
        fallback_reason="llm_failure",
        llm_failed=True,
    )

    assert metrics.used_fallback is True
    assert metrics.fallback_reason == "llm_failure"
    assert metrics.llm_failed is True

def test_successful_answer_has_no_fallback_reason():
    metrics = RAGMetrics(
        retrieved_chunks=1,
        retrieval_confidence=0.648,
        cited_chunks=1,
        used_fallback=False,
        fallback_reason=None,
        llm_failed=False,
    )

    assert metrics.used_fallback is False
    assert metrics.fallback_reason is None
    assert metrics.llm_failed is False


def test_metrics_reject_invalid_fallback_reason():
    with pytest.raises(ValidationError):
        RAGMetrics(
            retrieved_chunks=0,
            retrieval_confidence=0.0,
            cited_chunks=0,
            used_fallback=True,
            fallback_reason="unknown_reason",
            llm_failed=False,
        )


def test_metrics_reject_fallback_without_reason():
    with pytest.raises(ValidationError):
        RAGMetrics(
            retrieved_chunks=0,
            retrieval_confidence=0.0,
            cited_chunks=0,
            used_fallback=True,
            fallback_reason=None,
            llm_failed=False,
        )


def test_metrics_reject_llm_failure_with_wrong_reason():
    with pytest.raises(ValidationError):
        RAGMetrics(
            retrieved_chunks=1,
            retrieval_confidence=0.648,
            cited_chunks=0,
            used_fallback=True,
            fallback_reason="low_retrieval_confidence",
            llm_failed=True,
        )

def test_rag_pipeline_falls_back_when_llm_fails():
    fake_search_response = SimpleNamespace(
        results=[
            SimpleNamespace(
                chunk_id=10,
                document_id=20,
                similarity=0.90,
            )
        ]
    )

    with (
        patch(
            "app.services.chat_service.search_documents",
            return_value=fake_search_response,
        ),
        patch(
            "app.services.chat_service.build_rag_prompt",
            return_value="Test prompt",
        ),
        patch(
            "app.services.chat_service.ollama_client.generate",
            side_effect=LLMServiceError("Ollama unavailable"),
        ),
    ):
        fake_db = MagicMock()
        result = run_rag_pipeline(db=fake_db, question="How do I reset my password?")

    assert result.used_fallback is True
    assert result.llm_failed is True
    assert result.cited_chunk_ids == []

    assert result.metrics == RAGMetrics(
        retrieved_chunks=1,
        retrieval_confidence=0.90,
        cited_chunks=0,
        used_fallback=True,
        fallback_reason="llm_failure",
        llm_failed=True,
    )

#pytest tests/evaluation/test_evaluation.py -v