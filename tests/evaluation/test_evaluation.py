import sys
from pathlib import Path

EVALUATION_PATH = Path(__file__).parent
BACKEND_PATH = Path(__file__).parents[2] / "backend"

sys.path.insert(0, str(EVALUATION_PATH))
sys.path.insert(0, str(BACKEND_PATH))

from run_evaluation import (evaluate_citations, evaluate_expected_behavior)

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

#pytest tests/evaluation/test_evaluation.py -v