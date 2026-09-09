from app.llm.prompt_builder import build_rag_prompt
from app.schemas.search import SearchResult


results = [
    SearchResult(
        chunk_id=1,
        document_id=1,
        chunk_index=0,
        content=(
            "Customers can request a refund within "
            "30 days of the original purchase."
        ),
        similarity=0.89,
    )
]


prompt = build_rag_prompt(
    question="How long do I have to request a refund?",
    results=results,
)

print(prompt)