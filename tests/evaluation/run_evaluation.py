import json
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "test_cases.json"

def load_test_cases() -> list[dict]:
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)

def evaluate_expected_behavior(
    test_case: dict,
    actual_has_results: bool,
) -> bool:
    expected_behavior = test_case["expected_behavior"]

    if expected_behavior == "answer_from_knowledge_base ":
        return actual_has_results

    if expected_behavior == "fallback":
        return not actual_has_results

    raise ValueError(
        f"Unknown expected behavior: {expected_behavior}"
    )


if __name__ == "__main__":
    test_cases = load_test_cases()

    print(f"Loaded {len(test_cases)} evaluation cases:")

    for index, test_case in enumerate(
        test_cases, 
        start=1,
    ):
        print(
            f"{index}. "
            f"{test_case['question']} "
            f"-> "
            f"{test_case['expected_behavior']}"
        )