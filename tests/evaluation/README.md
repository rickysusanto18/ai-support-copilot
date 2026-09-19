# RAG Evaluation

This directory contains evaluation datasets and evaluation-related tests
for the AI Support Copilot.

Each evaluation case contains:
- A user question
- The expected system behavior

The evaluation dataset will be used to measure:
- Retrieval quality
- Fallback behavior
- Citation correctness
- Answer quality
- AI system reliability

To run the test, from your base directory, run:
python tests/evaluation/run_evaluation.py

Note: If you want a large dataset, it is available to download @ huggingface community 😊