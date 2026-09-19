import json
import sys
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "test_cases.json"
BACKEND_PATH = Path(__file__).parents[2] / "backend"

#MIN_RETRIEVAL_SIMILARITY = threshold (ubah sesuai kebutuhan)
#rumus: 
# if chunk = 0 then FAIL
# if chunk > 0: 
#   if similarity < threshold then FAIL 
#   if similarity >= threshold then PASS
MIN_RETRIEVAL_SIMILARITY = 0.50


sys.path.insert(
    0,
    str(BACKEND_PATH),
)

from app.db.database import SessionLocal
from app.services.retrieval_service import search_documents

def load_test_cases() -> list[dict]:
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)

def evaluate_expected_behavior(
    test_case: dict,
    actual_has_results: bool,
    top_similarity: float,
) -> bool:
    expected_behavior = test_case["expected_behavior"]

    if expected_behavior == "answer_from_knowledge_base":
        return (
            actual_has_results and 
            top_similarity >= MIN_RETRIEVAL_SIMILARITY
        )

    if expected_behavior == "fallback":
        return not actual_has_results

    raise ValueError(
        f"Unknown expected behavior: {expected_behavior}"
    )

def evaluate_test_case(
        test_case: dict,
) -> dict:
    db = SessionLocal()

    try:
        search_response = search_documents(
            db=db,
            query=test_case["question"],
            top_k=5,
            min_similarity=0.35,
        )

        actual_has_results = bool(
            search_response.results
        )

        top_similarity = (
            search_response.results[0].similarity
            if search_response.results
            else 0.0
        )

        passed = evaluate_expected_behavior(
            test_case=test_case,
            actual_has_results=actual_has_results,
            top_similarity=top_similarity,
        )

        return {
            "question": test_case["question"],
            "expected_behavior": test_case[
                "expected_behavior"
            ],
            "actual_has_results": actual_has_results,
            "retrieved_chunks": len(
                search_response.results
            ),
            "top_similarity": top_similarity,
            "passed": passed,
        }

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
            f"{status}: "
            f"{result['question']}"
        )

        print(
            f"  Expected: "
            f"{result['expected_behavior']}"
        )

        print(
            f"  Retrieved chunks: "
            f"{result['retrieved_chunks']}"
        )

        print(
            f"  Top similarity: "
            f"{result['top_similarity']:.3f}"
        )

    print_summary(results)