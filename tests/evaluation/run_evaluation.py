import json
import sys
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "test_cases.json"
BACKEND_PATH = Path(__file__).parents[2] / "backend"

sys.path.insert(0, str(BACKEND_PATH))

from app.db.database import SessionLocal
from app.services.retrieval_service import search_documents
from app.services.chat_service import run_rag_pipeline
from app.core.config import settings

def load_test_cases() -> list[dict]:
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)

# This function is to let the evaluation knows 3 scenarios:
# 1. Strong: Expected: answer, Similarity >= 0.50, PASS
# 2. Weak: Expected: fallback, Similarity < 0.50, PASS
# 3. None: Expected: fallback, No result, PASS
def evaluate_expected_behavior(
    test_case: dict,
    is_actual_has_result: bool,
    top_similarity: float,
) -> bool:
    expected_behavior = test_case["expected_behavior"]
    expected_retrieval = test_case["expected_retrieval"]

    if expected_retrieval == "strong":
        return (
            expected_behavior == "answer_from_knowledge_base" and 
            is_actual_has_result and 
            top_similarity >= settings.retrieval_min_similarity
        )

    if expected_retrieval == "weak_or_fallback":
        return (
            expected_behavior == "fallback" and (
                not is_actual_has_result or 
                top_similarity < settings.retrieval_min_similarity
            )
        )

    if expected_retrieval == "none":
        return (
            expected_behavior == "fallback" and 
            not is_actual_has_result
        )

    raise ValueError(
        f"Unknown retrieval expectation: {expected_retrieval}"
    )

# Detect whether LLM really take the chunk id from the given source or not
def evaluate_citation(
        retrieved_chunk_id: list[int],
        cited_chunk_id: list[int],
) -> bool:
    if not cited_chunk_id:
        return False

    retrieved_id = set(retrieved_chunk_id)
    cited_id = set(cited_chunk_id)

    return cited_id.issubset(retrieved_id)

# Temporary manual citation test
# if __name__ == "__main__":
#     print(
#         evaluate_citation(
#             retrieved_chunk_id=[10, 11, 12],
#             cited_chunk_id=[10, 12],
#         )
#     )

#     print(
#         evaluate_citation(
#             retrieved_chunk_id=[10, 11, 12],
#             cited_chunk_id=[99],
#         )
#     )

def evaluate_rag_pipeline(db, test_case: dict) -> dict:
    result = run_rag_pipeline(
        db=db, 
        question=test_case["question"],
    )

    behavior_passed = evaluate_expected_behavior(
        test_case=test_case,
        is_actual_has_result=bool(result.retrieved_chunk_id),
        top_similarity=result.retrieval_confidence,
    )

    citation_passed = True

    if test_case["expected_citation"]:
        citation_passed = evaluate_citation(
            retrieved_chunk_id=result.retrieved_chunk_id,
            cited_chunk_id=result.cited_chunk_id,
        )
    else:
        citation_passed = not result.cited_chunk_id

    return {
        "question": test_case["question"],
        "expected_behavior": test_case["expected_behavior"],
        "answer": result.answer,
        "retrieved_chunk": result.metrics.retrieved_chunk,
        "top_similarity": result.metrics.retrieval_confidence,
        "cited_chunk": result.cited_chunk_id,
        "is_used_fallback": result.metrics.is_used_fallback,
        "is_llm_failed": result.metrics.is_llm_failed,
        "behavior_passed": behavior_passed,
        "citation_passed": citation_passed,
        "passed": (behavior_passed and citation_passed),
        "fallback_reason": result.metrics.fallback_reason,
    }

def evaluate_test_case(test_case):
    db = SessionLocal()

    try:
        return evaluate_rag_pipeline(
            db=db,
            test_case=test_case,
        )
    finally:
        db.close()

def print_summary(results: list[dict]) -> None:
    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total - passed

    pass_rate = (
        passed / total
        if total > 0
        else 0.0
    )

    print()
    print("------------------")
    print("Evaluation Summary")
    print("------------------")
    print(f"Total cases: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {pass_rate:.1%}")


# for CI/CD
def validate_results(results: list[dict]) -> None:
    failed_results = [
        result
        for result in results
        if not result["passed"]
    ]

    if failed_results:
        raise SystemExit(
            f"{len(failed_results)} "
            "evaluation case failed"
        )

if __name__ == "__main__":
    test_cases = load_test_cases()

    print(
        f"Loaded {len(test_cases)} evaluation cases."
    )

    results = []

    for test_case in test_cases:
        result = evaluate_test_case(test_case)

        results.append(result)

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        print(
            f"{status}: {result['question']}"
        )

        print(
            f"  Expected: {result['expected_behavior']}"
        )

        print(
            f"  Retrieved chunk: {result['retrieved_chunk']}"
        )

        print(
            f"  Top similarity: {result['top_similarity']:.3f}"
        )

        print(
            f"  Cited chunk: {result['cited_chunk']}"
        )

        print(
            f"  Behavior: {'PASS' if result['behavior_passed'] else 'FAIL'}"
        )

        print(
            f"  Citations: {'PASS' if result['citation_passed'] else 'FAIL'}"
        )

        print(
            f"  Fallback: {result['is_used_fallback']}"
        )

        print(
            f"  LLM failed: {result['is_llm_failed']}"
        )

        print(
            f"  Fallback reason: {result['fallback_reason']}"
        )

    print_summary(results)
    validate_results(results)

def get_retrieved_chunk_id(search_response) -> list[int]:
    return [
        result.chunk_id
        for result in search_response.results
    ]