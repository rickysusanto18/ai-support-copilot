import json
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "test_cases.json"

def load_test_cases() -> list[dict]:
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


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

#Note: Compare actual behavior with expected behavior later on