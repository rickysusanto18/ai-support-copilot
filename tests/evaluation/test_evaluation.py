import sys
import pytest

from pathlib import Path
from pydantic import ValidationError
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

EVALUATION_PATH = Path(__file__).parent
BE_PATH = Path(__file__).parents[2] / "backend"

sys.path.insert(0, str(EVALUATION_PATH))
sys.path.insert(0, str(BE_PATH))

from run_evaluation import (evaluate_citation, evaluate_expected_behavior)
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
        is_actual_has_result=True,
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
        is_actual_has_result=True,
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
        is_actual_has_result=False,
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
        is_actual_has_result=True,
        top_similarity=0.80,
    )

    assert result is False

def test_citation_is_valid_when_chunk_was_retrieved():
    result = evaluate_citation(
        retrieved_chunk_id=[1, 2, 3],
        cited_chunk_id=[1, 3],
    )

    assert result is True

def test_citation_is_invalid_when_chunk_was_not_retrieved():
    result = evaluate_citation(
        retrieved_chunk_id=[1, 2, 3],
        cited_chunk_id=[99]
    )

    assert result is False

def test_no_context_records_correct_fallback_reason():
    metrics = RAGMetrics(
        retrieved_chunk=0,
        retrieval_confidence=0.0,
        cited_chunk=0,
        is_used_fallback=True,
        fallback_reason="no_relevant_context",
        is_llm_failed=False,
    )

    assert metrics.is_used_fallback is True
    assert metrics.fallback_reason == "no_relevant_context"
    assert metrics.is_llm_failed is False

def test_low_confidence_records_correct_fallback_reason():
    metrics = RAGMetrics(
        retrieved_chunk=1,
        retrieval_confidence=0.411,
        cited_chunk=0,
        is_used_fallback=True,
        fallback_reason="low_retrieval_confidence",
        is_llm_failed=False,
    )

    assert metrics.is_used_fallback is True
    assert metrics.fallback_reason == "low_retrieval_confidence"
    assert metrics.cited_chunk == 0

def test_llm_failure_records_correct_fallback_reason():
    metrics = RAGMetrics(
        retrieved_chunk=1,
        retrieval_confidence=0.648,
        cited_chunk=0,
        is_used_fallback=True,
        fallback_reason="llm_failure",
        is_llm_failed=True,
    )

    assert metrics.is_used_fallback is True
    assert metrics.fallback_reason == "llm_failure"
    assert metrics.is_llm_failed is True

def test_successful_answer_has_no_fallback_reason():
    metrics = RAGMetrics(
        retrieved_chunk=1,
        retrieval_confidence=0.648,
        cited_chunk=1,
        is_used_fallback=False,
        fallback_reason=None,
        is_llm_failed=False,
    )

    assert metrics.is_used_fallback is False
    assert metrics.fallback_reason is None
    assert metrics.is_llm_failed is False


def test_metrics_reject_invalid_fallback_reason():
    with pytest.raises(ValidationError):
        RAGMetrics(
            retrieved_chunk=0,
            retrieval_confidence=0.0,
            cited_chunk=0,
            is_used_fallback=True,
            fallback_reason="unknown_reason",
            is_llm_failed=False,
        )


def test_metrics_reject_fallback_without_reason():
    with pytest.raises(ValidationError):
        RAGMetrics(
            retrieved_chunk=0,
            retrieval_confidence=0.0,
            cited_chunk=0,
            is_used_fallback=True,
            fallback_reason=None,
            is_llm_failed=False,
        )


def test_metrics_reject_llm_failure_with_wrong_reason():
    with pytest.raises(ValidationError):
        RAGMetrics(
            retrieved_chunk=1,
            retrieval_confidence=0.648,
            cited_chunk=0,
            is_used_fallback=True,
            fallback_reason="low_retrieval_confidence",
            is_llm_failed=True,
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

    assert result.is_used_fallback is True
    assert result.is_llm_failed is True
    assert result.cited_chunk_id == []

    assert result.metrics == RAGMetrics(
        retrieved_chunk=1,
        retrieval_confidence=0.90,
        cited_chunk=0,
        is_used_fallback=True,
        fallback_reason="llm_failure",
        is_llm_failed=True,
    )

def test_evaluate_citations_rejects_unretrieved_chunk():
    retrieved_chunk_id = [10, 20]
    cited_chunk_id = [10, 99]

    assert evaluate_citation(retrieved_chunk_id, cited_chunk_id) is False

#pytest tests/evaluation/test_evaluation.py -v